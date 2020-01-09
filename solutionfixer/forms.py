from django import forms
from django.forms import ModelForm
from django.forms.widgets import TextInput, HiddenInput, CheckboxSelectMultiple, Select

from solutionfixer.models import Solution

#class AutocompleteSelectWidget(Widget):
#    def __init__(self, attrs={}):
#        super(Widget, self).__init__(attrs)
#        self.attrs = attrs or {}
#        self.textinput = TextInput()
#        self.hiddeninput = HiddenInput()
#        
#    def render(self, name, value, attrs=None):
#        output = []
#        output.append(self.textinput.render(name, value, attrs))
#        output.append(self.hiddeninput.render(name, value, attrs))
#        return mark_safe(u'\n'.join(output))
    
class SolventForm(forms.Form):
    solvent = forms.ChoiceField(
                choices=(
                         ('',''),
                         ('703','Propylene Glycol'),
                         ('321','Ethyl Alcohol'),
                         ('829','Triacetin'),
                         ('1983','Neobee'),
                         ('758','Soybean Oil'),
                         ('86','Benzyl Alcohol'),
                         ('100','Water'),
                         ('473','Liquid Lactic Acid'),
                         ('25','Iso Amyl Alcohol'),
                         ('782','Sugar'),
                         ('3','Silica'),
                         ('1432','Maltodextrin GMO'),
                         ('732','Salt regular'),
                         ('1478','Dextrose'),
                         ),)
    
class PercentageForm(forms.Form):
    percentage = forms.DecimalField(max_digits=4, decimal_places=2)

class SolutionStatusForm(forms.Form):
    status = forms.ChoiceField(
                choices=(
                         ('1','unverified'),
                         ('2','flagged'),
                         ('3','verified'),
                         ('3','remove from list'),
                         ),
                widget=forms.widgets.RadioSelect,
    )
    
class SolutionModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder= [
                               'my_base_autocomplete',
                               'percentage',
                               'solvent_choice',
                               'status',
                               ]
    solvent_choice = forms.ChoiceField(
                widget=forms.Select(attrs={'class':'solvent_selector'}),
                choices=(
                         ('',''),
                         ('703','Propylene Glycol'),
                         ('321','Ethyl Alcohol'),
                         ('829','Triacetin'),
                         ('1983','Neobee'),
                         ('758','Soybean Oil'),
                         ('86','Benzyl Alcohol'),
                         ('100','Water'),
                         ('473','Liquid Lactic Acid'),
                         ('25','Iso Amyl Alcohol'),
                         ('782','Sugar'),
                         ('3','Silica'),
                         ('1432','Maltodextrin GMO'),
                         ('732','Salt regular'),
                         ('1478','Dextrose'),
                         ),)
    my_base_autocomplete = forms.CharField(widget=forms.TextInput(attrs={'class':'my_base_autocomplete','size':'30'}))
    
    def as_tr(self, hidden=False):
        html_bits = []
#        if hidden:
#            html_bits.append(u'<tr id="%s" style="display: none"><td>%s</td>' % (self.prefix,self.instance.__str__()))
#        else:
        html_bits.append('<tr id="%s" class="%s"><td><a href="/access/ingredient/pin_review/%s/">%s</a></td>' % (self.prefix,
                                                                  self.instance.status.status_name,
                                                                  self.instance.ingredient.id,
                                                                  self.instance.__str__()))
        for_loop_is_first = True
        for field in self.visible_fields():
            html_bits.append('<td>')
            if (for_loop_is_first == True):
                for_loop_is_first = False
                for hidden_field in self.hidden_fields():
                    html_bits.append(hidden_field.__str__())
                html_bits.append(self['my_base'].__str__())
                html_bits.append(self['my_solvent'].__str__())
                html_bits.append('<span class="solution_id" style="display:none;">%s</span>' %
                                 self.instance.id)
            html_bits.append(field.__str__())
            html_bits.append('</td>')
        html_bits.append('</tr>')
        rendered_string = ''.join(html_bits)
        return rendered_string
        
    class Meta:
        model = Solution
        widgets = {
                   'ingredient':HiddenInput(),
                   'my_base':HiddenInput(attrs={'class':'my_base_hidden'}),
                   'my_solvent':HiddenInput(),
                   'percentage':TextInput(attrs={'size':'6','class':'percentage_input'}),
                   'status':Select(attrs={'class':'status_selector'}),
                   }
        exclude = () #('ingredient','my_base','my_solvent')

class SolutionFilterSelectForm(forms.Form):
    status = forms.MultipleChoiceField(
        widget=CheckboxSelectMultiple,
        required=False,
        choices=(
            ("unverified","unverified"),
            ("flagged","flagged"),
            ("verified","verified"),
        ),
        initial=("unverified","flagged","verified"))
    