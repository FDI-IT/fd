from django import template

from newqc.models import TestCard, ProductInfo
from newqc.forms import ResolveTestCardForm, ProductInfoForm

register = template.Library()

@register.inclusion_tag('qc/testcards/resolve_testcard_form.html')
def testcard_form(testcard,divclass=""):
    if testcard == None:
        return
    testcard_form = ResolveTestCardForm(instance=testcard)
    productinfo,created = ProductInfo.objects.get_or_create(flavor=testcard.retain.lot.flavor)
    productinfo_form = ProductInfoForm(prefix="product_info",instance=productinfo)
    return {'testcard_form':testcard_form,
            'productinfo_form':productinfo_form,
            'divclass':divclass}
    