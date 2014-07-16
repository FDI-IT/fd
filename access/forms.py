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

from access.models import Flavor, FlavorSpecification, Formula, ExperimentalLog, TSR, TSRLineItem, PurchaseOrderLineItem, Solvent, PurchaseOrder, NATART_CHOICES, Ingredient, get_next_rawmaterialcode, get_next_experimentalnum, ExperimentalFormula, SOLUBILITY_CHOICES, RISK_ASSESSMENT_CHOICES
from solutionfixer.models import SolutionStatus, Solution

def validate_ingredient_number(number):
    if Ingredient.objects.filter(id=number).count() == 0:
        raise ValidationError(u'PIN %s is not in the database.' % number)

def validate_formula_ingredient_number(number):
    try:
        Ingredient.get_formula_ingredient(number)
    except:
        raise ValidationError(u'%s is not a valid ingredient number' % number)
    
class FormulaIngredientField(forms.CharField):
    default_validators = [validate_formula_ingredient_number]

class IngredientField(forms.IntegerField):
    default_validators = [validate_ingredient_number]


class DigitizedFormulaPasteForm(forms.Form):
    paste = forms.CharField(widget=forms.Textarea)

class IngredientCostUpdate(forms.Form):
    new_cost = forms.FloatField()

class STLayoutForm(forms.Form):
    constrained = forms.BooleanField(required=False, initial=False)
    levels_to_show = forms.IntegerField(required=False, initial=10, max_value=9999, min_value=2)
    level_distance = forms.IntegerField(required=False, initial=30, max_value=1000,min_value=10)
    node_height = forms.IntegerField(required=False, initial=30, max_value=200,min_value=10)
    node_width = forms.IntegerField(required=False, initial=180, max_value=600,min_value=30)
    orientation = forms.ChoiceField(required=True, initial='left', choices=(('left','left'),('top','top')))
    
class TSRLIForm(ModelForm):
    def __init__(self, *args, **kwargs):
        try:
            my_content_type = kwargs['instance'].content_type.model
            
            
            if my_content_type == 'flavor':
                # set the initial value of self.content_type_select to flavor
                kwargs['initial'] = {'content_type_select': 'flavor'}
            if my_content_type == 'experimentallog':
                kwargs['initial'] = {'content_type_select': 'ex_log'}
        except:
            pass
    
        super(TSRLIForm, self).__init__(*args, **kwargs)

    class Meta:
        model = TSRLineItem
        exclude = ('content_type, object_id, product')
        
    TYPE = [('flavor', 'Flavor'),
            ('ex_log', 'Experimental Log')]
    content_type_select = forms.ChoiceField(choices=TYPE, widget=forms.RadioSelect())

def make_tsr_form(request): #using closure to obtain logged in user from request and save it in entered_by
    class TSRForm(ModelForm):
        
        class Meta:
            model = TSR
            exclude = ('date_in, entered_by')
        
        def save(self, commit=True):
            f = super(TSRForm, self).save(commit=False)
            if not f.pk:
                f.entered_by = request.user
            if commit: 
                f.save()
            return f
        
    return TSRForm
        
class PurchaseOrderForm(ModelForm):

    class Meta:
        model = PurchaseOrder
        exclude = (
                   'ship_to', 'memo', 'memo2'
                   )

class FlavorReviewForm(ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(FlavorReviewForm, self).__init__(*args, **kwargs)
        
        
    class Meta:
        model = Flavor
        fields = ('flashpoint','allergen','gmo','prop65','organic', 'no_pg',
                  'microtest','diacetyl','nutri_on_file','kosher',
                  'kosher_id','yield_field','reactionextraction',
                  'sulfites_ppm',
                  'batfno','haccp','ccp1','ccp2','ccp3','ccp4','ccp5','ccp6',
                  'organoleptics','color','spg',
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

class ExperimentalForm(ModelForm, FieldsetMixin):
    #product_name = forms.CharField(label="Experimental Name")
    fieldsets = (
         ('Hidden',{
            'fields': ('experimentalnum','product_name',
                       'datesent',
                       'initials','experimental_number','location_code_old',
                   'promotable', 'product_number',   'retain_number', 'retain_present','flavor',
                   'label_type','liquid',
                       'dry',
                       'spraydried',
                       'oilsoluble',
                       'concentrate',
                       'flavorcoat',
                       'na',
                       'natural',
                       'organic',
                       'wonf',
                       'artificial',
                       'nfi',
                       'natural_type',
                       'exclude_from_reporting',
                       ),
            'extra_content':{'divid':'hidden',
                             'legend':'Hidden'}
        }),
        ('Extended Info', {
            'fields': (
                       'customer',
                       'spg',
                       'flash',
                       'usagelevel',
                       'color',
                       'organoleptics',
                       'yield_field',
                       ),
            'extra_content':{'divid':'extendedinfo',
                             'legend':'Specs'},
        }),
        ('Duplication Info', {
            'fields': (
                       'duplication',
                       'duplication_company',
                       'duplication_name',
                       'duplication_id',
                       ),
            'extra_content':{'divid':'type',
                             'legend':'Duplication Info'},
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
                  'organic',
                  'natural_type',
                  'wonf',
                  'liquid',
                  'dry',
                  'spraydried',
                  'flavorcoat',
                  'concentrate',
                  'oilsoluble',
                  'unitprice',
                  'approved',
                  'organoleptics',
                  'color',
                  'yield_field',
                  'productmemo',
                  'pricing_memo',
                  'mixing_instructions',
                  
                  )

class FlavorSearch(forms.Form):
    search_string = forms.CharField(label="Search", required=False)

class IngredientReplacerForm(forms.Form):
    original_ingredient = IngredientField()
    new_ingredient = IngredientField()

class FormulaRow(forms.Form):
    ingredient_number = FormulaIngredientField(label="")
    amount = forms.DecimalField(label="", max_digits=9, decimal_places=5)
    ingredient_pk = forms.IntegerField(required=False)
    
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

def make_exclude_tuples(x): #Don't want to have a "None" option
    for y in x:
        yield(y,y)

class FormulaEntryExcludeSelectForm(forms.Form):
    allergen_choices = make_exclude_tuples(Ingredient.aller_attrs)
    allergen = forms.MultipleChoiceField(
        label="Allergens",
        widget=widgets.CheckboxSelectMultiple,
        required=False,
        choices=tuple(allergen_choices)
        )
    

class FormulaEntryFilterSelectForm(forms.Form):
    cursor = connection.cursor()
    cursor.execute('select distinct "Raw Materials"."ART_NATI" from "Raw Materials" ORDER BY "Raw Materials"."ART_NATI" ASC')
    natart_choices = []
    for choice in cursor.fetchall():
        natart_choices.append((choice[0], choice[0]))
        
    misc_choices = (
           # ('diacetyl','No Diacetyl'),
            ('prop65','No Prop65'),
            ('gmo','No GMO'),
           # ('no_pg', 'No PG'),
           # ('Organic','Organic')
        )
    
    misc = forms.MultipleChoiceField(
        label="Miscellaneous Properties",
        widget=widgets.CheckboxSelectMultiple,
        required=False,
        choices=misc_choices
        )


    allergen_choices = make_exclude_tuples(Ingredient.aller_attrs)
    allergen = forms.MultipleChoiceField(
        label="Allergens to Exclude",
        widget=widgets.CheckboxSelectMultiple,
        required=False,
        choices=tuple(allergen_choices)
        )
    
    art_nati = forms.MultipleChoiceField(
        label="Natural/Artificial",
        widget=widgets.CheckboxSelectMultiple,
        required=False,
        choices=tuple(natart_choices)
        )
    

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
    
class TSRFilterSelectForm(forms.Form):
    cursor = connection.cursor()
    cursor.execute('select distinct id, auth_user.username from auth_user ORDER BY auth_user.username ASC')
    user_choices = []
    
    for choice in cursor.fetchall():
        user_choices.append((choice[0], choice[1]))
        
    assigned_to = forms.MultipleChoiceField(
        widget=widgets.CheckboxSelectMultiple,
        required=False,
        choices=(tuple(user_choices))
        )

    other = forms.MultipleChoiceField(
        widget=widgets.CheckboxSelectMultiple,
        required=False,
        choices=(
            ('open', "Open TSRs"),
        ))

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
            ('spraydried', "Spray Dried"),
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
    for formula_row in Formula.objects.filter(flavor=flavor):
        formula_form_row = {}
        label_row = {}
        if formula_row.ingredient.is_gazinta:
            formula_form_row['ingredient_number'] = str(formula_row.ingredient.flavornum) + 'f'

        else:
            formula_form_row['ingredient_number'] = str(formula_row.ingredient.id)
        formula_form_row['ingredient_pk'] = formula_row.ingredient.pk
        formula_form_row['amount'] = str(formula_row.amount)
        label_row['cost'] = str(formula_row.get_exploded_cost().quantize(Decimal('.001'), rounding=ROUND_HALF_UP))
        label_row['name'] = formula_row.ingredient.long_name
        initial_data.append(formula_form_row)
        label_rows.append(label_row)
    return (initial_data, label_rows)

def build_formularow_formset_label_rows(formset):
    label_rows = []
    for form in formset.forms:
        label_row = {}
        if len(form._errors) == 0:
            try:
                ingredient = Ingredient.get_formula_ingredient(form.cleaned_data['ingredient_number'])
            except KeyError:
                continue
            try:
                amount = form.cleaned_data['amount']
            except KeyError:
                amount = 0
            
            try:
                label_row['cost'] = str((ingredient.unitprice*amount/1000).quantize(Decimal('.001'), rounding=ROUND_HALF_UP))
            except:
                label_row['cost'] = "---"
            try:
                label_row['name'] = ingredient.long_name
            except:
                label_row['name'] = "---"
        else:
            label_row['cost'] = "---"
            label_row['name'] = "---"
        label_rows.append(label_row)
    return label_rows

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
        return HttpResponseRedirect('/access/ingredient/pin_review/%s/' % i.id)
    
    
    
class NewExForm1(FormRequiredFields, FieldsetMixin):
    fieldsets = (
        ('Name',{
             'fields': ('natart', 'product_name',),
             'extra_content':{
                              'divid':'name_fields',
                              'legend':''
                              }
        }),
        ('Natural Categories',{
             'fields': ('wonf','natural_type','organic',),
             'extra_content':{
                              'divid':'natcat_fields',
                              'legend':'Natural Categories'
                              }
        }),  
        ('Physical Properties',{
             'fields': ('liquid','dry','spraydried','flavorcoat'),
             'extra_content':{
                              'divid':'physical_fields',
                              'legend':'Physical Properties - Required'
                              }
        }),
        ('Other',{
             'fields': ('concentrate','oilsoluble',),
             'extra_content':{
                              'divid':'other_fields',
                              'legend':'Other'
                              }
        }),
        ('Hidden',{
            'fields': ('label_type',),
            'extra_content':{'divid':'hidden',
                             'legend':'Hidden'}
        }),
    )

    
    natart = forms.ChoiceField(label="Nat/Art",
                        choices=(
                                 ('',''),
                                 ('N/A','N/A'),
                                 ('Art','Art'),
                                 ('Nat','Nat'),
                                 ('NFI','NFI'),
                                 ))
    product_name = forms.CharField(max_length=50) 
    wonf = forms.BooleanField(label="Natural WONF", required=False)
    natural_type = forms.BooleanField(label="Natural Type", required=False)
    organic = forms.BooleanField(label="Organic Compliant", required=False)
    flavorcoat = forms.BooleanField(label="Flavorcoat", required=False)
    liquid = forms.BooleanField(required=False)
    dry = forms.BooleanField(required=False)
    spraydried = forms.BooleanField(required=False)
    concentrate = forms.BooleanField(required=False)
    oilsoluble = forms.BooleanField(label="Oil Soluble", required=False)
    label_type = forms.CharField(max_length=50,required=False)
    natart_processor = {
        'N/A':'na',
        'Art':'artificial',
        'Nat':'natural',
        'NFI':'nfi',           
    }
    
    def process_data(self, experimental, ):
        kvlist = []
        
        for k,v in self.cleaned_data.iteritems():
            kvlist.append((k,v))
            setattr(experimental, k, v)
        experimental.na = False
        experimental.natural = False
        experimental.artificial = False
        experimental.nfi = False
        setattr(experimental, self.natart_processor[self.cleaned_data['natart']], True)
        return experimental
    
class NewExForm2(FormRequiredFields):
    memo = forms.CharField(widget=forms.Textarea,required=False)
    customer = forms.CharField(max_length=30)
    duplication = forms.BooleanField(required=False)
    duplication_company = forms.CharField(max_length=50,required=False)
    duplication_name = forms.CharField(max_length=50,required=False)
    duplication_id = forms.CharField(max_length=50,required=False)
    promotable = forms.BooleanField(required=False)
    holiday = forms.BooleanField(required=False)
    chef_assist = forms.BooleanField(required=False)
    
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
    def get_template(self, step):
        return ['access/experimental/wizard_%s.html' % step, 'forms/wizard.html']
    
    def done(self, request, form_list):
        ex = ExperimentalLog()
        for form in form_list[1:]:
            for k,v in form.cleaned_data.iteritems():
                setattr(ex,k,v)
        form_list[0].process_data(ex)
        ex.experimentalnum = get_next_experimentalnum()
        ex.datesent = datetime.now()
        ex.initials = "%s%s" % (request.user.first_name[0], request.user.last_name[0])
        f = Flavor(number=Flavor.get_next_tempex_number(),
                   name=ex.product_name,
                   prefix='EX',
                   natart=ex.natart,
                   experimental=ex.experimentalnum,
                   label_type=ex.label_type,
                   yield_field=ex.yield_field,
                   )
        f.save()
        ex.flavor = f
        ex.save()
             
        return HttpResponseRedirect('/access/experimental/%s/' % ex.experimentalnum)

class ExperimentalNameForm(NewExForm1):
    pass    


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
    solvent = forms.ModelChoiceField(queryset=Solvent.objects.all())

    

# def validate_spec_name(name):
#     if FlavorSpecification.objects.filter(name=name).count() != 0:
#         raise ValidationError(u'A specification with that name already exists.')

    
# class CustomerSpecificationNameField(forms.CharField):
#     default_validators = [validate_spec_name]


#use closure to get the flavor for which the form is being used
def make_flavorspec_form(flavor):
    class FlavorSpecificationForm(forms.Form):
        pk = forms.IntegerField(initial=0)
        name = forms.CharField(max_length=48, required=True)
        specification = forms.CharField(max_length=48, required=True)
        micro = forms.BooleanField(required=False, initial=False)
    #     customer_id = forms.IntegerField(initial=0, widget = forms.TextInput(attrs={'readonly':'readonly'}))
    #     replaces_id = forms.IntegerField(initial=0, widget = forms.TextInput(attrs={'readonly':'readonly'}))
        #result = forms.CharField(max_length=48)
        def clean(self):
            cleaned_data = self.cleaned_data
            pk = cleaned_data.get("pk")
            name = cleaned_data.get("name").lstrip().rstrip() #get rid of accidental spaces before and after name
            delete = cleaned_data.get(u'DELETE')
            
            if delete == False:
                if FlavorSpecification.objects.filter(flavor=flavor).filter(name=name).exclude(pk=pk).exists():
                    raise ValidationError("A specification with the name '%s' already exists" % name)
      
            return cleaned_data    
    
    
    return FlavorSpecificationForm


#use closure to get the flavor for which the form is being used; flavor is used in validation
def make_customerspec_form(flavor):
    class CustomerSpecificationForm(forms.Form):
        pk = forms.IntegerField(initial=0)
        name = forms.CharField(max_length=48, required=True)
        specification = forms.CharField(max_length=48, required=True)
        micro = forms.BooleanField(required=False)
        
        def clean(self):
            cleaned_data = self.cleaned_data
            pk = cleaned_data.get("pk")
            name = cleaned_data.get("name").lstrip().rstrip() #get rid of accidental spaces before and after name

            if FlavorSpecification.objects.filter(flavor=flavor).filter(name=name).exclude(pk=pk).exists():
                raise ValidationError("A specification with the name '%s' already exists" % name)

       
            return cleaned_data    
    
    
    return CustomerSpecificationForm    

class ReconciledSpecForm(forms.Form):
    name = forms.CharField(max_length=48, required=True, widget = forms.TextInput(attrs={'readonly':'readonly'}))
    specification = forms.CharField(max_length=48, required=True)

class GHSReportForm(forms.Form):
    
    REPORT_CHOICES = [('GHS_Exclusive_Ingredients', 'GHS Exclusive Ingredients'),
                      ('FDI_Exclusive_Ingredients', 'FDI Exclusive Ingredients')]
    
    report_to_download = forms.ChoiceField(required=True, choices=REPORT_CHOICES, widget=forms.RadioSelect())
    

class CasFemaSpreadsheetFileForm(forms.Form):
    file = forms.FileField()
                                                                   

