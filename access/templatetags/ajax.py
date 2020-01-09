from decimal import Decimal, ROUND_HALF_UP

from django import template
from django.urls import reverse
from django.db.models import Sum

from access.models import Flavor, FormulaTree, Ingredient, FormulaException, FormulaCycleException
from access.utils import coster_headers
from itertools import chain

register = template.Library()

template_paths = {
        'consolidated':'access/flavor/consolidated.html',
        'explosion':'access/flavor/explosion.html',
        'production_lots':'access/flavor/production_lots.html',
        'retains':'access/flavor/retains.html',
        'raw_material_pin':'access/ingredient/raw_material_pin.html',
        'gzl_ajax':'access/gzl_ajax.html',
    }

@register.inclusion_tag(template_paths['consolidated'])
def consolidated(flavor, weight_factor=1):
    return {'flavor':flavor,
            'test':1}

@register.inclusion_tag(template_paths['explosion'])
def explosion(flavor, weight_factor=1):
    fts = FormulaTree.objects.filter(root_flavor=flavor)[1:]
    close_div_stack = []
    hypertext_tokens = []
    hypertext_tokens.append(
        """
        <table id="explosion-divs">
        <thead>
            <tr>
                <th width=45%>Name</th>
                <th>Type</th>
                <th>Last Update</th>
                <th>Unit Cost</th>
                <th>Amount</th>
                <th>Relative Cost</th>
            </tr>
        </thead>
        </table>
        """
    )
    for ft in fts:
        look_at_stack = True
        while(1):
            if look_at_stack == False:
                break
            try:
                if ft.lft > close_div_stack[-1]:
                    hypertext_tokens.append("</div>\n")
                    close_div_stack.pop()
                else:
                    look_at_stack = False
            except IndexError:
                break
        
        if ft.rgt > ft.lft+1:
            link_token = '<a href="#" onclick="return hideftrow(this)">[+]</a> '
            row_class = 'ft-expander-row'
            label_type = 'Flavor'
        else:
            link_token = ''
            row_class = 'ft-simple-row'
            label_type = 'Raw material'
        
        
        hypertext_tokens.append(
            """<div class="%s">%s%s <span class="ingredient-details"><span class="fttype">%s</span> 
                                                                        <span class="ftupdate">%s</span> 
                                                                        <span class="ftunitcost">%s</span> 
                                                                        <span class="ftamount" data-ogw="%s">%s</span> 
                                                                        <span class="ftrelcost">%s</span>
                                        </span></div>\n""" % (row_class, 
                                                              link_token, 
                                                              ft.node_ingredient,
                                                              label_type,
                                                              ft.node_ingredient.purchase_price_update.date(),
                                                              ft.node_ingredient.unitprice,
                                                              ft.weight,
                                                              ft.weight,
                                                              ft.weight)
            )
        
        if ft.rgt > ft.lft+1:
            close_div_stack.append(ft.rgt)
            hypertext_tokens.append('<div class="ft-spacer">\n')
    for close_div in close_div_stack:
        hypertext_tokens.append("</div>\n")
    return {"flavor":flavor,
            "ft": "".join(hypertext_tokens),
            "stack_leftovers": close_div_stack,
            "headers":coster_headers}

@register.inclusion_tag(template_paths['production_lots'])
def production_lots(flavor):
    object_list = flavor.lot_set.all()
    return {'object_list':object_list,}

@register.inclusion_tag(template_paths['retains'])
def retains(product):
    object_list = product.sorted_retain_superset()
    return {'object_list':object_list,}

@register.inclusion_tag(template_paths['raw_material_pin'])
def raw_material_pin(flavor):
    g = flavor.gazinta.all()[0]
    ingredients = Ingredient.objects.filter(id=g.id)
    return {'ingredients':ingredients,}

@register.inclusion_tag(template_paths['gzl_ajax'])
def gzl_ajax(flavor):
    return {'gt':FormulaTree.objects.filter(node_flavor=flavor).exclude(root_flavor=flavor).values('root_flavor__number').annotate(Sum('weight')).order_by('-weight'),}
