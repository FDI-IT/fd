from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP

from django import forms
from django.http import HttpResponseRedirect
from django.forms import ModelForm
from django.forms.models import BaseModelFormSet
from django.contrib.formtools.wizard import FormWizard
from django.contrib import admin
from django.forms import widgets
from django.db import connection
from django.core.exceptions import ValidationError

from formfieldset.forms import FieldsetMixin

from access.models import Flavor, Formula, ExperimentalLog, PurchaseOrderLineItem, PurchaseOrder, NATART_CHOICES, Ingredient, get_next_rawmaterialcode, get_next_experimentalnum, ExperimentalFormula, SOLUBILITY_CHOICES, RISK_ASSESSMENT_CHOICES
from solutionfixer.models import SolutionStatus, Solution

def validate_ingredient_number(number):
    if Ingredient.objects.filter(id=number).count() == 0:
        raise ValidationError(u'PIN %s is not in the database.' % number)

class IngredientField(forms.IntegerField):
    default_validators = [validate_ingredient_number]


class DigitizedFormulaPasteForm(forms.Form):
    paste = forms.CharField(widget=forms.Textarea)

class IngredientCostUpdate(forms.Form):
    new_cost = forms.FloatField()

class PurchaseOrderForm(ModelForm):

    class Meta:
        model = PurchaseOrder
        exclude = (
                   'ship_to', 'memo', 'memo2'
                   )

class FlavorReviewForm(ModelForm):
    class Meta:
        model = Flavor
        fields = ('flashpoint','allergen','gmo','prop65','organic', 'no_pg',
                  'microtest','diacetyl','nutri_on_file','kosher',
                  'kosher_id','yield_field','reactionextraction',
                  'sulfites_ppm',
                  'batfno','haccp','ccp1','ccp2','ccp3','ccp4','ccp5','ccp6'
                  )
        widgets = {'kosher':widgets.TextInput(),}
        
#        exclude = ('id','number','ingredients','solvent','name',
#                   'prefix','code','natart','label_type','categoryid',
#                   'unitprice','quantityperunit','supplierid',
#                   'unitsinstock','unitsonorder','reorderlevel',
#                   'discontinued','approved','productmemo','sold',
#                   'lastprice','experimental','lastspdate','rawmaterialcost',
#                   'valid','solubility','nutri_on_file','flammability',
#                   'pinnumber','vaporpressure','crustacean','eggs','fish',
#                   'milk','peanuts','soybeans','treenuts','wheat','sulfites',
#                   'entered','sunflower','sesame','mollusks','mustard','celery',
#                   'lupines','yellow_5'       
#                   )

class FlavorForm(ModelForm):
    solvent = forms.ChoiceField(
                    choices=(
                             ('',''),
                             ('PG','Propylene Glycol'),
                             ('Ethyl Alcohol','Ethyl Alcohol'),
                             ('Triacetin','Triacetin'),
                             ('Neobee','Neobee'),
                             ('Water','Water'),
                             ('Soybean Oil','Soybean Oil'),
                             ('N/A - Powder','N/A - Powder'),
                             ),)
    natart = forms.ChoiceField(
                    choices=(
                             ('',''),
                             ('Nat','Natural'),
                             ('Art','Artificial'),
                             ('N/A','Natural / Artificial'),
                             ('NI','Nature Identical'),
                             ('NFI','Non-Flavor Ingredient'),
                             ),)
    label_type = forms.ChoiceField(
                    choices=(
                             ('',''),
                             ('Flavor','Flavor'),
                             ('Type Flavor','Type Flavor'),
                             ('Flavor WONF','Flavor WONF'),
                             ('Concentrate','Concentrate'),
                             ('Type Concentrate','Type Concentrate'),
                             ('Concentrate WONF','Concentrate WONF'),
                             ('OC Flavor','OC Flavor'),
                             ('OC Type Flavor','OC Type Flavor'),
                             ('OC Flavor WONF','OC Flavor WONF'),
                             ('OC Concentrate','OC Concentrate'),
                             ('OC Type Concentrate','OC Type Concentrate'),
                             ('OC Concentrate WONF','OC Concentrate WONF'),
                             ),)

    class Meta:
        model = Flavor
        exclude = ('id','ingredients','categoryid',
                   'supplierid','unitsinstock','unitsonorder',
                   'reorderlevel','discontinued','approved',
                   'sold','lastprice','lastspdate',
                   'rawmaterialcost','productmemo','valid',
                   'quantityperunit','code', 'name',
                   'experimental','unitprice','spraydried',
                   'prefix'
                   )
        
class ExperimentalFlavorForm(FlavorForm):
    class Meta:
        model = Flavor
        exclude = ('id','ingredients','categoryid',
                   'supplierid','unitsinstock','unitsonorder',
                   'reorderlevel','discontinued','approved',
                   'sold','lastprice','lastspdate',
                   'rawmaterialcost','productmemo','valid',
                   'quantityperunit','code', 'name',
                   'experimental','unitprice','spraydried',
                   'prefix','number',
                   )
        
class ExperimentalForm(ModelForm, FieldsetMixin):
    #product_name = forms.CharField(label="Experimental Name")
    fieldsets = (
        ('Extended Info', {
            'fields': ('product_name',
                       'customer',
                       'spg',
                       'flash',
                       'usagelevel',
                       'color',
                       'organoleptics',
                       ),
            'extra_content':{'divid':'extendedinfo',
                             'legend':'Specs'},
        }),
        ('Type', {
            'fields': ('liquid',
                       'dry',
                       'spray_dried',
                       'oilsoluble',
                       'concentrate',
                       'duplication',
                       ),
            'extra_content':{'divid':'type',
                             'legend':'Type'},
        }),
        ('Label', {
            'fields': ('na',
                       'natural',
                       'organic',
                       'wonf',
                       ),
            'extra_content':{'divid':'label',
                             'legend':'Label'},
        }),
        ('Product Application & Usage', {
            'fields': ('holiday',
                       'tea',
                       'coffee',
                       'fruit',
                       'nutraceutical',
                       'meat_and_savory',
                       'chai',
                       'baked_goods',
                       'dairy',
                       'snacks',
                       'non_food',
                       'flavor_coat',
                       'sweet',
                       'personal_care',
                       'beverage',
                       'pet',
                       'tobacco',
                       'chef_assist',),
            'extra_content':{'divid':'prodapp',
                             'legend':'Product Application & Usage'},
        }),
        ('Memo',{
            'fields': ('memo',
                       'mixing_instructions'),
            'extra_content':{'divid':'memo',
                             'legend':'Memo'}
        }),
        ('Hidden',{
            'fields': ('experimentalnum',
                       'datesent',
                       'initials','experimental_number',
                       
                   'promotable', 'product_number',   'retain_number', 'retain_present','flavor',
                       ),
            'extra_content':{'divid':'hidden',
                             'legend':'Hidden'}
        }),
    )
    
    class Meta:
        model = ExperimentalLog
        exclude = ('ingredients','natart')

class ApproveForm(ModelForm):
    class Meta:
        model = Flavor
        fields = (
                  'prefix',
                  'number',
                  'natart',
                  'name',
                  'label_type',
                  'unitprice',
                  'approved',
                  'productmemo',
                  )

class FlavorSearch(forms.Form):
    search_string = forms.CharField(label="Search", required=False)


class IngredientReplacerForm(forms.Form):
    original_ingredient = IngredientField()
    new_ingredient = IngredientField()

class FormulaRow(forms.Form):
    ingredient_number = forms.CharField(label="")
    amount = forms.DecimalField(label="", max_digits=9, decimal_places=5)
    
class ExperimentalFormulaRow(forms.Form):
    ingredient_number = forms.CharField(label="")
    amount = forms.DecimalField(label="", max_digits=9, decimal_places=5)

class LocationEntryForm(forms.Form):
    flavor_number = forms.CharField(label="")
    location_code = forms.CharField(label="")
    
class POLIForm(ModelForm):
    class Meta:
        model = PurchaseOrderLineItem
        widgets = {
            'raw_material': forms.HiddenInput(attrs={'size':'40'}),
        }
        exclude=("due_date","purchase_price","legacy_purchase","date_received")
        
class BaseFormulaFormSet(BaseModelFormSet):
    def clean(self):
        super(BaseFormulaFormSet, self).clean()
        total = 0
        for form in self.forms:
            try:
                total += form.cleaned_data['amount']
            except KeyError:
                pass
        if total != 1000:
            raise forms.ValidationError, "Formula does not add up to 1000"
        
    def __init__(self, *args, **kwargs):
        super(BaseFormulaFormSet, self).__init__(*args, **kwargs)
        
class BaseIngredientFormSet(BaseModelFormSet):
    def clean(self):
        super(BaseIngredientFormSet, self).clean()
    
    def __init__(self, *args, **kwargs):
        super(BaseIngredientFormSet, self).__init__(*args, **kwargs)
        
    def save_existing(self, form, instance, commit=True):
        instance.purchase_price_update = datetime.now()
        return BaseModelFormSet.save_existing(self, form, instance, commit)


class IngredientFilterSelectForm(forms.Form):
    cursor = connection.cursor()
    cursor.execute('select distinct "Raw Materials"."ART_NATI" from "Raw Materials" ORDER BY "Raw Materials"."ART_NATI" ASC')
    natart_choices = []
    for choice in cursor.fetchall():
        natart_choices.append((choice[0], choice[0]))
        
    cursor.execute('select distinct "Raw Materials"."KOSHER" from "Raw Materials" ORDER BY "Raw Materials"."KOSHER" ASC')
    kosher_choices = []
    for choice in cursor.fetchall():
        kosher_choices.append((choice[0], choice[0]))
        
    discontinued= forms.MultipleChoiceField(
        widget=widgets.CheckboxSelectMultiple,
        required=False,
        choices=(
            (True,"Active"),
            (False,"Discontinued"),
        ))
    art_nati = forms.MultipleChoiceField(
        widget=widgets.CheckboxSelectMultiple,
        required=False,
        choices=(tuple(natart_choices))
        )
    kosher = forms.MultipleChoiceField(
        widget=widgets.CheckboxSelectMultiple,
        required=False,
        choices=(tuple(kosher_choices))
        )
    
class PurchaseOrderFilterSelectForm(forms.Form):
    pass


class FlavorFilterSelectForm(forms.Form):
    cursor = connection.cursor()
    cursor.execute('select distinct access_integratedproduct.natart from access_integratedproduct ORDER BY access_integratedproduct.natart ASC')
    natart_choices = []
    for choice in cursor.fetchall():
        natart_choices.append((choice[0], choice[0]))
        
    cursor.execute('select distinct access_integratedproduct.kosher from access_integratedproduct ORDER BY access_integratedproduct.kosher ASC')
    kosher_choices = []
    for choice in cursor.fetchall():
        kosher_choices.append((choice[0], choice[0]))
        
    cursor.execute('select * from "flavor_usage_applicationtype"')
    appl_choices = []
    for choice in cursor.fetchall():
        appl_choices.append((choice[0], choice[1]))
        
    valid = forms.MultipleChoiceField(
        widget=widgets.CheckboxSelectMultiple,
        required=False,
        choices=(
            (True,"Valid"),
            (False,"Invalid"),
        ))
    approved = forms.MultipleChoiceField(
        widget=widgets.CheckboxSelectMultiple,
        required=False,
        choices=(
            (True,"Approved"),
            (False,"Not Approved"),
        ))
    sold = forms.MultipleChoiceField(
        widget=widgets.CheckboxSelectMultiple,
        required=False,
        choices=(
            (True,"Sold"),
            (False,"Not Sold"),
        ))
    natart = forms.MultipleChoiceField(
        widget=widgets.CheckboxSelectMultiple,
        required=False,
        choices=(tuple(natart_choices))
        )
    
    other = forms.MultipleChoiceField(
        widget=widgets.CheckboxSelectMultiple,
        required=False,
        choices=(
            ('no_pg', "No PG"),
            ('retains__notes', "Retains On File"),
            ('supportive_potential', "Supportive Potential"),
        ))

    application = forms.MultipleChoiceField(
        widget=widgets.CheckboxSelectMultiple,
        required=False,
        choices=(tuple(appl_choices))
        )
    
    kosher = forms.MultipleChoiceField(
        widget=widgets.CheckboxSelectMultiple,
        required=False,
        choices=(tuple(kosher_choices))
        )
    
    risk_assessment_group = forms.MultipleChoiceField(
        widget=widgets.CheckboxSelectMultiple,
        required=False,
        choices=RISK_ASSESSMENT_CHOICES,                                              
        )
    
class ExperimentalFilterSelectForm(forms.Form):
    cursor = connection.cursor()
    cursor.execute('select distinct "ExperimentalLog"."Initials" from "ExperimentalLog" ORDER BY "ExperimentalLog"."Initials" ASC')
    initials_choices = []
    for choice in cursor.fetchall():
        initials_choices.append((choice[0], choice[0]))
        
    initials = forms.MultipleChoiceField(
        widget=widgets.CheckboxSelectMultiple,
        required=False,
        choices=(tuple(initials_choices))
        )
    
    cursor.execute('select distinct "ExperimentalLog".natart from "ExperimentalLog" ORDER BY "ExperimentalLog".natart ASC')
    natart_choices = []
    for choice in cursor.fetchall():
        natart_choices.append((choice[0], choice[0]))
    natart = forms.MultipleChoiceField(
        widget=widgets.CheckboxSelectMultiple,
        required=False,
        choices=(tuple(natart_choices))
        )
    
    other = forms.MultipleChoiceField(
        widget=widgets.CheckboxSelectMultiple,
        required=False,
        choices=(
            ('liquid', "Liquid"),
            ('dry', "Dry"),
            ('spray_dried', "Spray Dried"),
            ('oilsoluble', "Oil Soluble"),
            ('concentrate', "Concentrate"),
    ))
    
def build_poli_formset_initial_data(po):
    initial_data = []
    label_rows = []
    polis = PurchaseOrderLineItem.objects.filter(po=po)
    for poli in polis:
        poli_row = {}
        label_row = {}
        poli_row['ingredient_number'] = str(poli.raw_material.rawmaterialcode)
        poli_row['quantity'] = str(poli.quantity)
        poli_row['package_size'] = str(poli.package_size)
        label_row['total_size'] = str(poli.quantity * poli.package_size)
        label_row['price'] = str(poli.raw_material.unitprice * poli.quantity * poli.package_size)
        label_row['name'] = "%s - %s" % (poli.raw_material.id, poli.raw_material.product_name)
        initial_data.append(poli_row)
        label_rows.append(label_row)
    return (initial_data, label_rows)
        
def build_formularow_formset_initial_data(flavor):
    initial_data = []
    label_rows = []
    ingredients = Formula.objects.filter(flavor=flavor)
    for ingredient in ingredients:
        formula_row = {}
        label_row = {}
        if ingredient.ingredient.is_gazinta:
            formula_row['ingredient_number'] = str(ingredient.ingredient.flavornum) + 'f'
        else:
            formula_row['ingredient_number'] = str(ingredient.ingredient.id)
        formula_row['amount'] = str(ingredient.amount)
        label_row['cost'] = str(ingredient.get_exploded_cost().quantize(Decimal('.001'), rounding=ROUND_HALF_UP))
        label_row['name'] = ingredient.ingredient.product_name
        initial_data.append(formula_row)
        label_rows.append(label_row)
    return (initial_data, label_rows)

def build_experimental_formularow_formset_initial_data(experimental):
    initial_data = []
    label_rows = []
    ingredients = ExperimentalFormula.objects.filter(experimental_log=experimental)
    for ingredient in ingredients:
        formula_row = {}
        label_row = {}
        if ingredient.ingredient.is_gazinta:
            formula_row['ingredient_number'] = str(ingredient.ingredient.flavornum) + 'f'
        else:
            formula_row['ingredient_number'] = str(ingredient.ingredient.id)
        formula_row['amount'] = str(ingredient.amount)
        label_row['cost'] = str(ingredient.get_exploded_cost().quantize(Decimal('.001'), rounding=ROUND_HALF_UP))
        label_row['name'] = ingredient.ingredient.product_name
        initial_data.append(formula_row)
        label_rows.append(label_row)
    return (initial_data, label_rows)

class FormRequiredFields(forms.Form):
    required_css_class = 'required_field'

#Raw Material Entry Wizard
class NewRMForm1(FormRequiredFields):
    art_nati = forms.ChoiceField(choices=(('',''),) + NATART_CHOICES)
    prefix = forms.CharField(max_length=60,required=False)    
    product_name = forms.CharField(max_length=60)
    part_name2 = forms.CharField(max_length=60, required=False)
    memo = forms.CharField(widget=forms.Textarea, required=False)
    description = forms.CharField(max_length=60, required=False)
    
class NewRMForm11(FormRequiredFields):
    solubility = forms.ChoiceField(choices=(('',''),) + SOLUBILITY_CHOICES)
    solubility_memo = forms.CharField(max_length=50,required=False)
    comments = forms.CharField(label="Comments (Organoleptics)",widget=forms.Textarea,required=False)
    
class NewRMForm2(FormRequiredFields):
    unitprice = forms.DecimalField(label="Unit Price (dollars)",max_digits=10,decimal_places=3,min_value=0)
    purchase_price_update = forms.DateField(initial=date.today, widget=admin.widgets.AdminDateWidget())
    suppliercode = forms.CharField(label="Supplier", max_length=50)
    supplier_catalog_number = forms.CharField(max_length=50,required=False)
    package_size = forms.DecimalField(label="Package size (pounds)",max_digits=7,decimal_places=2,min_value=0)
    minimum_quantity = forms.DecimalField(label="Minimum quantity (pounds)", max_digits=7,decimal_places=2,min_value=0)
    quantity_discount = forms.CharField(max_length=50,required=False)
    fob_point = forms.CharField(max_length=50)
    lead_time = forms.CharField(max_length=50)
    
class NewRMForm3(FormRequiredFields):
    kosher = forms.CharField(max_length=20, required=False)
    kosher_code = forms.CharField(max_length=50, required=False)
    lastkoshdt = forms.DateField(initial=datetime(1990,1,1), label="Last Kosher Date", widget=admin.widgets.AdminDateWidget())
    
class NewRMForm4(FormRequiredFields):
    cas = forms.CharField(max_length=15, required=False)
    fema = forms.CharField(max_length=15, required=False)
    natural_document_on_file = forms.BooleanField(required=False)
    hazardous = forms.TypedChoiceField(coerce=lambda x: bool(int(x)),
                                            choices=((0,"No"),(1,"Yes")),
                                            widget=forms.RadioSelect)
    microsensitive = forms.TypedChoiceField(coerce=lambda x: bool(int(x)),
                                            choices=((0,"No"),(1,"Yes")),
                                            widget=forms.RadioSelect)
    prop65 = forms.TypedChoiceField(coerce=lambda x: bool(int(x)),
                                            choices=((0,"No"),(1,"Yes")),
                                            widget=forms.RadioSelect)
    nutri = forms.TypedChoiceField(coerce=lambda x: bool(int(x)),
                                            choices=((0,"No"),(1,"Yes")),
                                            widget=forms.RadioSelect)

def make_two_tuple_from_list(x):
    yield("None","None")
    for y in x:
        yield(y,y)


class NewRMForm5(FormRequiredFields):
    sulfites_ppm = forms.DecimalField(min_value=0,max_value=1000000, decimal_places=1, max_digits=6)
    allergens = forms.MultipleChoiceField(
        widget=widgets.CheckboxSelectMultiple,
        choices=make_two_tuple_from_list(Ingredient.aller_attrs))
    
    def clean_allergens(self):
        data = self.cleaned_data['allergens']
        if "None" in data:
            if len(data) > 1:
                raise forms.ValidationError('Cannot have "None" and %s allergens' % ', '.join(data[1:]))
            else:
                return []
        return data
    
class NewRMWizard(FormWizard):
    def done(self, request, form_list):
        i = Ingredient()
        form_5 = form_list.pop()
        allergens = form_5.cleaned_data['allergens']
        for allergen in allergens:
            setattr(i,allergen,True)
        sulfites_ppm = form_5.cleaned_data['sulfites_ppm']
        if sulfites_ppm == 0:
            setattr(i, 'sulfites', False)
        else:
            setattr(i, 'sulfites', True)
        setattr(i, 'sulfites_ppm', sulfites_ppm)
        for form in form_list:
            for k,v in form.cleaned_data.iteritems():
                setattr(i,k,v)
        
        i.id = get_next_rawmaterialcode()
        i.rawmaterialcode = i.id
        i.discontinued = True
        if i.memo != "":
            i.memo = "%s - Entered by %s" % (i.memo, request.user.username)
        else:
            i.memo = "Entered by %s" % request.user.username 
        if 'extra_rm' in self.initial:
            e = self.initial['extra_rm']
            i.id = e['id']
    
        if 'extra_flavor' in self.initial:
            e = self.initial['extra_flavor']
            f = Flavor.objects.get(id=e['sub_flavor_id'])
            f.pinnumber = i.id
            f.save()
            i.sub_flavor = f
            i.flavornum = e['flavornum']
            i.solubility = 'Other - see memo'
            i.solubility_memo = e['solubility_memo']
            i.discontinued = False
        i.save()
        if 'extra_solution' in self.initial:
            e = self.initial['extra_solution']
            i.discontinued=False
            s = Solution(ingredient=i,
                         my_base_id=e['my_base_pk'],
                         my_solvent_id=e['my_solvent_pk'],
                         percentage=e['solution'],
                         status=SolutionStatus.objects.get(status_name__iexact="verified"))
            s.save()
            i.save()
        return HttpResponseRedirect('/django/access/ingredient/pin_review/%s/' % i.id)
    
    
    
class NewExForm1(FormRequiredFields):
    customer = forms.CharField(max_length=30)
    product_name = forms.CharField(max_length=50)
    memo = forms.CharField(widget=forms.Textarea,required=False)
    
class NewExForm2(FormRequiredFields):
    liquid = forms.BooleanField(required=False)
    dry = forms.BooleanField(required=False)
    spray_dried = forms.BooleanField(required=False)
    concentrate = forms.BooleanField(required=False)
    oilsoluble = forms.BooleanField(required=False)
    na = forms.BooleanField(required=False)
    natural = forms.BooleanField(required=False)
    organic = forms.BooleanField(required=False)
    wonf = forms.BooleanField(required=False)
    duplication = forms.BooleanField(required=False)
    promotable = forms.BooleanField(required=False)
    holiday = forms.BooleanField(required=False)
    chef_assist = forms.BooleanField(required=False)
    flavor_coat = forms.BooleanField(required=False)
    
class NewExForm3(FormRequiredFields):    
    coffee = forms.BooleanField(required=False)
    tea = forms.BooleanField(required=False)
    fruit = forms.BooleanField(required=False)
    sweet = forms.BooleanField(required=False)
    nutraceutical = forms.BooleanField(required=False)
    personal_care = forms.BooleanField(required=False)
    meat_and_savory = forms.BooleanField(required=False)
    beverage = forms.BooleanField(required=False)
    chai = forms.BooleanField(required=False)
    baked_goods = forms.BooleanField(required=False)
    dairy = forms.BooleanField(required=False)
    pet = forms.BooleanField(required=False)
    snacks = forms.BooleanField(required=False)
    tobacco = forms.BooleanField(required=False)
    non_food = forms.BooleanField(required=False)
    
class NewExFormWizard(FormWizard):
    def done(self, request, form_list):
        ex = ExperimentalLog()
        for form in form_list:
            for k,v in form.cleaned_data.iteritems():
                setattr(ex,k,v)
        ex.experimentalnum = get_next_experimentalnum()
        ex.datesent = datetime.now()
        ex.initials = "%s%s" % (request.user.first_name[0], request.user.last_name[0])
        f = Flavor(number=Flavor.get_next_tempex_number(),
                   name=ex.product_name,
                   prefix='EX',
                   natart=ex.natart[:3],
                   experimental=ex.experimentalnum,
                   )
        f.save()
        ex.flavor = f
        ex.save()
        
        
        return HttpResponseRedirect('/django/access/experimental/%s/' % ex.experimentalnum)
    
class NewSolutionForm(forms.Form):
    PIN = forms.CharField()
    concentration = forms.ChoiceField(
                        choices=(
                                 ('',''),
                                 ('0.01%','0.01%'),
                                 ('0.05%','0.05%'),
                                 ('0.1%','0.1%'),
                                 ('0.2%','0.2%'),
                                 ('0.5%','0.5%'),
                                 ('1%','1%'),
                                 ('2%','2%'),
                                 ('5%','5%'),
                                 ('10%','10%'),
                                 ('25%','25%'),
                                 ('50%','50%'),
                                 ))
    solvent = forms.ChoiceField(
                    choices=(
                             ('',''),
                             ('703','Propylene Glycol'),
                             ('321','Ethyl Alcohol'),
                             ('829','Triacetin'),
                             ('1983','Neobee'),
                             ('100','Water'),
                             ('86','Benzyl Alcohol'),
                             ('473','Lactic Acid'),
                             ('25','Iso Amyl Alcohol'),
                             ('S758','Soybean Oil'),
                             ),)
   