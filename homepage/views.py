from django.shortcuts import render_to_response
from django.template import RequestContext

def index(request):
    return render_to_response('homepage/index.html',
                              context_instance=RequestContext(request))
    
def vanilla(request):
    return render_to_response('homepage/vanilla.html',
                              context_instance=RequestContext(request))

