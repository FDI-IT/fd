from django import template
from fd.access.models import Flavor
from fd.access import utils

register = template.Library()

@register.tag
def explode(parser, token):
    
    try:
        tag_name, flavor_id = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]
    
    return ExploderNode(flavor_id)
    
class ExploderNode(template.Node):
    def __init__(self, flavor_id):
        self.flavor_id = template.Variable(flavor_id)
                
    def render(self, context):
        flavor = Flavor.objects.get(id=self.flavor_id.resolve(context))
        exploder = utils.Exploder(flavor)
        
        return exploder.explode()
