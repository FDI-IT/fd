import operator
import re
from decimal import Decimal, InvalidOperation
from collections import deque

from django.conf import settings
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.utils import DatabaseError, IntegrityError
from django.db.models import Q

from access.models import Flavor, Ingredient, FormulaException, ExperimentalLog
from access import models
from access.csv_parse import parse_csv_field, FormulaBuilder, IngredientBuilder, ExperimentalBuilder, generic_exception_handle, ExceptionCSVWriter, RowMunger, NoRelationBuilder

from solutionfixer.models import Solution, SolutionStatus

#from one_off.migration_utils import dictify_flavors_by_number

coster_headers = (
                  ('ing_prefix','Pf','WIDTH=20 title="Two-character prefix"'),
                  ('ing_num_link','Num','WIDTH=20 title="Flavor Number"'),
                  ('ingredient_natart','N-A','WIDTH=26 title="Nat-Art Label"'),
                  ('ingredient_name','Name',''),
                  ('ingredient_type', 'Type', 'WIDTH=80'),
                  ('last_price_update', 'Update', 'WIDTH=60 title="Last Date When Price Changed"'),
                  ('unit_cost', 'Unit Cost', 'WIDTH=55 title="Ingredient Unit Cost"'),
                  ('rel_weight', 'Amount', 'WIDTH=55 title="Amount In Flavor"'),
                  ('rel_cost', 'Rel. Cost', 'WIDTH=55 title="Relative Cost of Raw Material in Finished Product"'),                
                  )


def build_cache():
    gazinta_lists = {}
    flavor_valid = set()
    for f in Flavor.objects.all():
        try:
            gazinta_lists[f.id] = f.gazinta.all()[0].formula_set.values('flavor_id','amount')  
        except IndexError:
            pass
        if f.valid:
            flavor_valid.add(f.id)
            
    return (gazinta_lists, flavor_valid)
            
            
class ImportData:
    def import_data(self, model_list):
        for model in model_list:
            print "Deleting %s records..." % model
            model.objects.all().delete()
        
        for model in model_list:
            print "Importing %s records..." % model
            self.import_model_data(model)
            """
            Models need a "access_table_name" field to indicate which table
            is the source of data of the model.
            """
            
            
    @transaction.commit_manually
    def import_model_data(self, model):
        # find certain model classes that need real relationships added
        if str(model) == str(models.Formula):
            relation_processor = FormulaBuilder()
        elif str(model) == str(models.ExperimentalLog):
            relation_processor = ExperimentalBuilder()
#        elif str(model) == str(models.ProductSpecialInformation):
#            relation_processor = ProductSpecialInformationBuilder()
        elif str(model) == str(models.Ingredient):
            relation_processor = IngredientBuilder()
        else:
            relation_processor = NoRelationBuilder()
        
        # create all the objects I need
        model_munger = RowMunger(model, settings.CSVSOURCE_PATH)
        model_exception_writer = \
            ExceptionCSVWriter(model, model_munger.header_row)
        model_field_map = model_munger.field_map
        
        sid_counter = 0
        # iterate over each row in the csv file
        for csv_row in model_munger:
            sid = transaction.savepoint()
            model_instance = model()
            try:
                #for each field in the row, set the model attribute
                for (csv_index, model_field) in model_field_map:
                    csv_field = unicode.strip(csv_row[csv_index])             
                    parsed_csv_field = \
                        parse_csv_field(model_field.db_type(), csv_field)
                    setattr(model_instance,
                        model_field.attname,
                        parsed_csv_field)                            
                      
                relation_processor.build_relation(model_instance)
                model_instance.save()
            except IntegrityError as e:
                transaction.savepoint_rollback(sid)
                print "%s %s -> %s" % (str(model), 
                                   str(model_munger.line_num()), 
                                   csv_row)
                generic_exception_handle(e, 
                                     csv_row, 
                                     model_exception_writer, 
                                     model) 
            except DatabaseError as e:
                transaction.savepoint_rollback(sid)
                raise e
            except Exception as e:
                transaction.savepoint_rollback(sid)
                print "%s %s -> %s" % (str(model), 
                                   str(model_munger.line_num()), 
                                   csv_row)
                generic_exception_handle(e, 
                                     csv_row, 
                                     model_exception_writer, 
                                     model)
                
            sid_counter+=1
            if sid_counter > 100:
                transaction.commit()
                sid_counter = 0
        transaction.commit()
        model_exception_writer.close()

class UpdateData:
    def update_data(self, model_list):
        for model in model_list:
            print "Updating %s..." % model
            self.update_model(model)
    
    
    @transaction.commit_manually
    def update_model(self, model):
        if model == Ingredient:
            self.relation_processor = IngredientBuilder()
            self.flag_stat = SolutionStatus.objects.get(status_name="flagged")
            previous_solution_count = Solution.objects.all().count()
        else:
            self.relation_processor = NoRelationBuilder()
        
        self.model = model
        self.debug = False
        self.resemble_count = 0
        self.new_count = 0
        self.different_count = []
        self.exception_count = 0
        self.model_munger = RowMunger(model, settings.CSVSOURCE_PATH)
        self.model_field_map = self.model_munger.field_map
        model_exception_writer = \
            ExceptionCSVWriter(model, self.model_munger.header_row)

        sid_counter = 0
        first_sid = transaction.savepoint()
        
        for csv_row in self.model_munger:
            sid = transaction.savepoint()
            sid_counter+=1
            try:
                self.process_row(csv_row)
            except ValidationError as e:
                self.exception_count += 1
                transaction.savepoint_rollback(sid)
                print "%s %s -> %s" % (str(self.model), 
                                   str(self.model_munger.line_num()), 
                                   csv_row)
                generic_exception_handle(e, 
                                     csv_row,
                                     model_exception_writer, 
                                     Flavor)
            except FormulaException as e:
                print "Formula Exception: %s" % e
                transaction.savepoint_rollback(sid)
                print "%s: %s -> %s" % (str(model), str(self.model_munger.line_num()), 
                                   csv_row)
                generic_exception_handle(e, 
                                     csv_row, 
                                     model_exception_writer, 
                                     Ingredient)
            except InvalidOperation as e:
                print "Invalid Operation: %s" % e
                transaction.savepoint_rollback(sid)
                print "%s: %s -> %s" % (str(model), str(self.model_munger.line_num()), 
                                   csv_row)
                generic_exception_handle(e, 
                                     csv_row, 
                                     model_exception_writer, 
                                     Ingredient)
            except DatabaseError as e:
                transaction.savepoint_rollback(sid)
                raise e
            except Exception as e:
                self.exception_count+=1
                transaction.savepoint_rollback(sid)
                print "%s: %s -> %s" % (str(model), str(self.model_munger.line_num()), 
                                   csv_row)
                generic_exception_handle(e, 
                                     csv_row, 
                                     model_exception_writer, 
                                     Ingredient)
                raise e
            if sid_counter > 200:
                transaction.commit()
                sid_counter = 0
            
            if model == Ingredient:
                if previous_solution_count != Solution.objects.all().count():
                    if self.debug:
                        transaction.savepoint_rollback(first_sid)
                        import pdb; pdb.set_trace()
        transaction.commit()
        model_exception_writer.close()
        
        print "Resembles: %s" % self.resemble_count
        print "Different: %s" % len(self.different_count)
        print "Exceptions: %s" % self.exception_count
        print "New: %s" % self.new_count
    
    
    def process_row(self, csv_row): 
        new_model_instance = self.model()
        #for each field in the row, set the model attribute
        for (csv_index, model_field) in self.model_field_map:
            csv_field = unicode.strip(csv_row[csv_index])        
            parsed_csv_field = parse_csv_field(model_field.db_type(), csv_field)
            setattr(new_model_instance,
                model_field.attname,
                parsed_csv_field)  
                                
        self.relation_processor.build_relation(new_model_instance)
            
        try:
            if self.model == Ingredient:
                old_model_instance = Ingredient.objects.get(pk=new_model_instance.pk)
            elif self.model == Flavor:
                old_model_instance = Flavor.objects.get(number=new_model_instance.number)
        except:
            new_model_instance.save()
            self.new_count += 1
            return
        new_model_instance.clean_fields()
        
        # diff field is the name of a field, or true if there are no differences
        difference_field = new_model_instance.resembles(old_model_instance)
        if (difference_field == True):
            self.resemble_count+=1
            new_model_instance.pk = old_model_instance.pk
            new_model_instance.save()
        else:
            new_model_instance.pk = old_model_instance.pk
            new_model_instance.save()
            self.different_count.append(difference_field)
            print u"Difference in %s - old: %s | new: %s" % (
                                            old_model_instance,
                                            getattr(old_model_instance, difference_field),
                                            getattr(new_model_instance, difference_field))
            
            if self.model == Ingredient:
                solutions_to_flag = Solution.objects.filter(Q(ingredient=old_model_instance) | 
                                                            Q(my_base=old_model_instance) |
                                                            Q(my_solvent=old_model_instance))
                for soluflag in solutions_to_flag:
                    soluflag.status=self.flag_stat
                    soluflag.save()
            
            
            
            
            

class IntegrityCheck:
    """Puts all flavors in a deque for validation. A flavor is popped from
    the deque and validation attempted. One of three cases can happen:
        Success: the flavor validates successfully, valid set to True
        Fail: flavor is not valid, and the status is set to a message why 
            validation failed
        Can't tell yet: The flavor can't be validated yet; it's re-appended 
            to validate on another pass
    """
    def __init__(self, flavors_to_validate_list=None):
        self.debug = True
        if flavors_to_validate_list is None:
            init_list = Flavor.objects.all()[:]
            self.flavors_to_validate_list = init_list
            self.iterated_over_all_flavors = True
        else:
            self.flavors_to_validate_list = flavors_to_validate_list
            self.iterated_over_all_flavors = False
        """A list of the flavors to validate, in order; the queryset is
        cached because it is used to initialize other objects.""" 
        
        self.flavors_to_validate = deque(self.flavors_to_validate_list)
        """The main structure over which we are iterating"""
        
        self.pass_count = 1
        """Keeps track of the number of passes through 
        self.flavors_to_validate
        """
        
        self.iter_count = 0
        """The number of times an element was examined 
        from self.flavors_to_validate
        """
        
        self.enqueued_flavors = set(self.flavors_to_validate_list)
        """A set of the flavors in the above deque, for quick inside lookups"""
        
        self.queue_extension_lists = {}
        """This dict is to apply a basic sorting on elements before they are
        re-appended to flavors_to_validate. Keys are the number of gazintas
        a flavor has. The reasoning is that the more gazintas, the later
        in the queue the flavor is appended, because maybe the gazintas will
        be pre-validated. This is flushed to flavors_to_validate whenever a 
        deque-pass has been finished."""
        
        self.validation_order = []
        """The order in which flavors were successfully validated from the 
        deque"""
        
        self.validated_flavors = {}
        """A dictionary of flavors that have been validated and their 
        validation status"""
        
        self.last_pass = False
        """Set to true when self.finish_pass determines that further passes
        will be ineffective at validating flavors."""
        
        
    def enqueue_flavor(self, f, formula_rows=None):
        """Adds f to a buffer to flush when the tail of
        self.flavors_to_validate is reached.
        """
        #if f not in self.enqueued_flavors
        #if gazinta not in self.enqueued_flavors:
        if formula_rows is None:
            formula_rows = f.formula_set.all()
        if f not in self.enqueued_flavors:
            gazinta_counter = formula_rows.filter(~Q(ingredient__sub_flavor=None))
            self.enqueued_flavors.add(f)
            self.queue_extension_lists.setdefault(gazinta_counter, []).append(f)
        
        
    def write_flavor_validation(self,f,validation_status,rmc=None):
        """Finalies the proper state of everything when an element
        successfully validates and does NOT need to be re-enqueued.
        """
        if f not in self.validated_flavors:
            self.validated_flavors[f] = (validation_status,rmc)
            self.validation_order.append(f)
        
        
    def validate(self, f):
        f_formula_rows = f.formula_set.all()
        validation_messages = []
        if f_formula_rows.count() == 0:
            self.write_flavor_validation(f, "Contains no ingredients.")
            return "Contains no ingredients."

        amount = 0
        rmc = 0
        contains_unknown_gazinta = False
        for fr in f_formula_rows:
            amount += fr.amount
            try:
                rmc += fr.get_exploded_cost()
            except RuntimeError:
                validation_messages.append("Cycle found")
                break
            gazinta = fr.ingredient.gazinta()
            if gazinta is None:
                continue
            validity_of_gazinta, gz_rmc = self.validated_flavors.get(gazinta,(None,None))
            if validity_of_gazinta is None:
                contains_unknown_gazinta = True
                self.enqueue_flavor(gazinta)
                continue
            elif validity_of_gazinta is True:
                continue
            else:
                validation_messages.append("Contains invalid gazinta: %s." % gazinta)

        if amount != Decimal(1000):
            validation_messages.append("Formula adds up to %s." % str(amount))
        
        if len(validation_messages) == 0:
            if contains_unknown_gazinta:
                self.enqueue_flavor(f, formula_rows=f_formula_rows)
                return False
            else:
                return self.write_flavor_validation(f, True, rmc)
        else:
            validation_status = "%s - %s" % (f, " | ".join(validation_messages))
            self.write_flavor_validation(f, validation_status)
            return validation_status
        
        
    def close_queue(self):
        """Finalizes the proper state of everything when
        self.flavors_to_validate is exhausted. 
        """
        for f in self.flavors_to_validate:
            self.write_flavor_validation(f,"Unable to validate; unknown reason.")
            
        for f in self.validation_order:
            validation_status, rmc = self.validated_flavors[f]
            if validation_status == True:
                f.valid = True
            else:
                f.valid = False
            if rmc is None:
                f.valid = False
            f.rawmaterialcost = rmc
            f.save()
            
            
    def start_pass(self):
        """Begins a pass of iterating through self.flavors_to_validate.
        Currently not decoupled from the actual iteration.
        """
        self.queue_len_at_beginning_of_pass = len(self.enqueued_flavors)
        while(True):
            try:
                f = self.flavors_to_validate.popleft()
                self.enqueued_flavors.remove(f)
            except:
                if self.finish_pass():
                    break
            self.iter_count += 1
            if self.debug:
                print "pass count: %s | iterations: %s | remaining this pass: %s | queue length: %s" % (
                    self.pass_count,
                    self.iter_count,
                    len(self.flavors_to_validate), 
                    len(self.enqueued_flavors))
            self.validate(f)
                
    
    
    def finish_pass(self):
        """Finalizes the proper state of everything when the tail of
        self.flavors_to_validate is reached.
        """
        #import pdb; pdb.set_trace()
        self.pass_count += 1
        # flush self.queue_extension_lists
        for key in sorted(self.queue_extension_lists.iterkeys()):
            extender = self.queue_extension_lists[key]
            self.flavors_to_validate.extend(extender)
        self.queue_extension_lists = {}
        
        # check if the queue length has changed since the last pass; 
        # if it has not, run one last pass the set the validation status
        # of the remaining flavors to failed because repeated passes are
        # ineffective (they most likely contain cycles.
        if (self.queue_len_at_beginning_of_pass == len(self.enqueued_flavors)):
            if self.last_pass:
                # TROUBLE when finish_pass reaches this code path, it ultmately
                # is done iterating
                self.close_queue()
                return True
            else:
                # TROUBLE this code path runs when another pass needs to get started
                self.last_pass = True
        self.queue_len_at_beginning_of_pass = len(self.enqueued_flavors)
        return False
    
class SolventUpdater():
    # the list definition of which raw material numbers represent solvents
    OIL_SOLVENTS = (1983, 829, 86)
    WATER_SOLVENTS = (703, 321, 100, 473, 25)
    ALL_SOLVENTS = OIL_SOLVENTS + WATER_SOLVENTS
    SOLVENT_NAMES = {
        1983:'Neobee',
        829:'Triacetin',
        86:'Benzyl Alcohol',
        703:'PG',
        321:'ETOH',
        100:'Water',
        473:'Lactic Acid',
        25:'Iso Amyl Alcohol',
    }

    def re_init(self):
        self.visited_flavors = {}
    
    
    def update_all_flavor_solvents(self):
        """
        """
        self.visited_flavors = {}
        self.all_flavors = Flavor.objects.filter(valid=True)
        for flavor in self.all_flavors:
            try:
                self.update_flavor_solvent(flavor)
            except FormulaException as e:
                print "Invalid flavor %s: %s" % (flavor, e)
    
    
    def update_flavor_solvent(self, flavor):
        my_solvents = {}
        for leaf_weight in flavor.leaf_weights.filter(ingredient__id__in=self.ALL_SOLVENTS).order_by('-weight'):
            ingredient = leaf_weight.ingredient
            ingredient_number = ingredient.id
            my_solvents[ingredient_number] = leaf_weight.weight
                
        ones = Decimal('1')
        sorted_solvent_string_list = []
        
        sorted_by_weight = sorted(my_solvents.iteritems(), key=operator.itemgetter(1))
        sorted_by_weight.reverse()
        
        for solvent_number, solvent_amount in sorted_by_weight:
            if solvent_amount > 0:
                relative_solvent_amount = (solvent_amount / 10).quantize(ones)                
                sorted_solvent_string_list.append("%s %s%%" % (self.SOLVENT_NAMES[solvent_number], relative_solvent_amount))
            
        solvent_string = "; ".join(sorted_solvent_string_list)
        flavor.solvent = solvent_string[:50]
        flavor.save()


# old stuff 
                
class OCUpdate():
    def update_all_oc(self):
        self.visited_flavors = {}
        self.all_flavors = Flavor.objects.filter(valid=True)
        for flavor in self.all_flavors:
            self.update_oc(flavor)
            
    def update_oc(self, flavor):
        name = flavor.name
        if re.search(r"\b[Oo]\.*[Cc]\.*\b", name):
            print name    
            
            
class MemoAnalyzer():
    def __init__(self):
        pass
    
    def analyze_flavor(self, f):
        return re.sub('(\d{3,})', r'<a href="/django/access/\1/">\1</a>', f.productmemo)
        
        
def renumber_finder():
    examined_falvors = set()
    memo_re = re.compile('Same as([0-9 ,]+)',re.IGNORECASE)
    
    def renumber_list(f, lots):
        if f in examined_flavors:
            return []
        examined_flavors.add(f)
        
        flavor_list = []
        
        match = memo_re.search(f.productmemo)
        if match:
            matched_string = match.group(1)
            number_list = []
            
            for x in matched_string.split(','):
                try:
                    number_list.append(int(x))
                except ValueError:
                    continue
            for flavor_number in number_list:
                try:
                    new_flavor = Flavor.objects.get(number=flavor_number)
                    flavor_list.append(new_flavor)
                except Flavor.DoesNotExist:
                    continue

        try:
            formula_rows = f.formula_set.all()
            if formula_rows.count() == 1:
                flavor_list.append(formula_rows[0].ingredient.sub_flavor)
        except:
            pass
        
        try:
            i = f.gazinta.all()[0]
            for formula in Formula.objects.filter(ingredient=i, amount=1000):
                flavor_list.append(formula.flavor)
        except IndexError:
            pass

        return flavor_list
    
    for f in Flavor.objects.filter(valid=True):
        lots = f.lot_set.none()
        inner_merge_lot_list(f, lots)
        
        
def analyze_antiseptic_ingredients():
    for f in Flavor.objects.all():
        f.supportive_potential=True
        f.save()
        
    for antiseptic_ingredient in models.AntisepticIngredient.objects.all():
        matching_ingredients = models.Ingredient.objects.filter(id=antiseptic_ingredient.pin)
        for i in matching_ingredients:
            matching_leaf_weights = models.LeafWeight.objects.filter(ingredient=i).filter(weight__gte=antiseptic_ingredient.concentration*10)
            for mlw in matching_leaf_weights:
                mlw.root_flavor.supportive_potential = False
                mlw.root_flavor.save()
                
def parse_experimental_natarts():
    for el in ExperimentalLog.objects.all():
        if el.na:
            if el.natural or el.organic or el.wonf:
                el.natart = "!!!"
            el.natart = "N/A"
        else:
            natart = []
            if el.natural:
                natart.append("Nat")
            if el.organic:
                natart.append("Org")
            if el.wonf:
                natart.append("WONF")
            el.natart = " ".join(natart)
        el.initials = el.initials.upper()
        el.save()
        