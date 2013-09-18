from decimal import Decimal, ROUND_HALF_UP

from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django import template
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.template import RequestContext

from access.models import Flavor, FormulaTree, Ingredient, FormulaException, FormulaCycleException
from access.utils import coster_headers
from itertools import chain
from reversion.models import Revision

register = template.Library()

@register.inclusion_tag('access/flavor/consolidated.html')
def consolidated(flavor, weight_factor=1):
    return {'flavor':flavor}

@register.inclusion_tag('access/flavor/explosion.html')
def explosion(flavor, weight_factor=1):
    fts = FormulaTree.objects.filter(root_flavor=flavor)[1:]
    close_div_stack = []
    hypertext_tokens = []
    hypertext_tokens.append(
        """
        <table id="explosion-divs">
        <thead>
            <tr>
                <th width=53%>Name</th>
                <th>Amount</th>
                <th>Unit Cost</th>
                <th>Relative Cost</th>
                <th>Last Update</th>
            </tr>
        </thead>
        </table>
        """
    )
    depth=0
    for ft in fts:
        look_at_stack = True
        while(1):
            if look_at_stack == False:
                break
            try:
                if ft.lft > close_div_stack[-1]:
                    hypertext_tokens.append("</div>\n")
                    close_div_stack.pop()
                    depth = depth -1
                else:
                    look_at_stack = False
            except IndexError:
                break
        
        if ft.rgt > ft.lft+1:
            link_token = '<a href="#" onclick="return hideftrow(this)">[+]</a> '
            row_class = 'ft-expander-row'
            label_type = 'Flavor'
            my_pin = ""
        else:
            link_token = ''
            row_class = 'ft-simple-row'
            label_type = 'Raw material'
            my_pin = ft.node_ingredient.id
        
        
        hypertext_tokens.append(
            """<div class="%s" data-ingredient_id="%s" data-nat_art="%s" data-ingredient_pin="%s" data-ingredient_name="%s"><span class="ingredient_name recur_depth_%s">%s%s</span> <span class="ingredient-details">
                                                                        <span class="ftamount" data-ogw="%s">%s</span> 
                                                                        <span class="ftunitcost">%s</span>                                                            
                                                                        <span class="ftrelcost">%s</span>
                                                                        <span class="ftupdate">%s</span> 
                                        </span></div>\n""" % (row_class,
                                                              ft.node_ingredient.id,
                                                              ft.node_ingredient.art_nati,
                                                              my_pin,
                                                              ft.node_ingredient.name,
                                                              depth, 
                                                              link_token,
                                                              ft.node_ingredient.name,
                                                              ft.weight,
                                                              ft.weight,
                                                              ft.node_ingredient.unitprice,
                                                              Decimal(str(ft.weight*ft.node_ingredient.unitprice/1000)).quantize(Decimal('0.00')),
                                                              ft.node_ingredient.purchase_price_update.date(),)
            )
        
        if ft.rgt > ft.lft+1:
            close_div_stack.append(ft.rgt)
            hypertext_tokens.append('<div class="ft-spacer">\n')
            depth=depth+1
    for close_div in close_div_stack:
        hypertext_tokens.append("</div>\n")
    return {"flavor":flavor,
            "ft": "".join(hypertext_tokens),
            "stack_leftovers": close_div_stack,
            "headers":coster_headers}

@register.inclusion_tag('access/flavor/production_lots.html')
def production_lots(flavor):
    object_list = flavor.lot_set.all()
    return {'object_list':object_list,}

@register.inclusion_tag('access/flavor/retains.html')
def retains(product):
    object_list = product.sorted_retain_superset()
    return {'object_list':object_list,}

@register.inclusion_tag('access/ingredient/raw_material_pin.html')
def raw_material_pin(flavor):
    g = flavor.gazinta.all()[0]
    ingredients = Ingredient.objects.filter(id=g.id)
    return {'ingredients':ingredients,}

@register.inclusion_tag('access/flavor/gzl_ajax.html')
def gzl_ajax(flavor):
    return {'gt':FormulaTree.objects.filter(node_flavor=flavor).exclude(root_flavor=flavor).values('root_flavor__number').annotate(Sum('weight')).order_by('-weight'),}

@register.inclusion_tag('history_audit/revision_history.html')
def revision_history(flavor):
    
    revision_rows = []
    
    resultant_objects = Revision.objects.filter(version__object_id = flavor.pk).filter(version__content_type__id=23).distinct().order_by('-date_created')
            
    for r in resultant_objects:
        v = r.version_set.all().get(object_id=flavor.pk)
        try:
            object = v.content_type.model_class().objects.get(pk=v.object_id)
            url = reverse('admin:%s_%s_change' %(object._meta.app_label, object._meta.module_name), args=[object.id]) + 'history'
            version_url = url
        except:
            version_url = 0
        
        revision_rows.append((r.date_created, v, version_url, r.version_set.all().count(), r.comment, r.user, r.id))

    
    return {        
        'revision_rows': revision_rows,
    }

    
    
    
    
    





