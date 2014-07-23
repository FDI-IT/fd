from django.forms import widgets
from django.utils.safestring import mark_safe
from django.utils.encoding import StrAndUnicode, force_unicode

# Inherit from a widget that's similar to what you want,
# and change the renderer to attribute to your own renderer.
#
# For the renderer, inherit from the renderer that's normally
# used, and override the render method.
#
# This overrides the RadioSelect widget and replaces it with
# one that puts radio buttons in cells of the same row:

class RetainStatusChangeRenderer(widgets.RadioFieldRenderer):
    def render(self):
        """Outputs table cells for this set of radio fields."""
        return mark_safe(u'%s' % u'\n'.join([u'<td class="qcradiobutton">%s</td>'
                % force_unicode(w) for w in self]))

class RetainStatusChangeWidget(widgets.RadioSelect):
    renderer = RetainStatusChangeRenderer

    #def render(self, name, value, attrs=None, choices=()):
    #    return super(forms.widgets.RadioSelect,self).render( name, value, attrs, choices) 

