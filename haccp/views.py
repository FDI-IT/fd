from django.shortcuts import render_to_response, get_object_or_404

from haccp import models

def index(request):
    return render_to_response('haccp/index.html')



cipm_list_info =  {
    'queryset': models.CIPM.objects.all(),
    'paginate_by': 100,
    'extra_context': dict({
        'page_title': 'Continuous Improvement and Preventative Maintenance',

    }),
}

def cipm_detail(request, cipm_pk):
    cipm = get_object_or_404(models.CIPM, pk=cipm_pk)
    return render_to_response('haccp/cipm_detail.html',{'cipm':cipm})