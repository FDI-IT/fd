"""Middleware used by Reversion."""

from django.http import HttpResponse, HttpResponseRedirect
from django.template.base import TemplateSyntaxError
from django.db.models.fields import FieldDoesNotExist
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError

class MyMiddleware(object):
    
    def process_exception(self, request, exception):
        if type(exception) == FieldDoesNotExist or type(exception) == ValidationError:
        #if type(exception) == TemplateSyntaxError:
            # = exception.exc_info
            #print exc_info
            #response = HttpResponse("Exception details: %s" % request.get_full_path())
            #return response
        
            url = request.get_full_path()
            
            version_pk = url.split('/')[-2]
            
            try:
                return HttpResponseRedirect(reverse('version_redirect', args=[version_pk, 'True']))
            except:
                pass
        
        