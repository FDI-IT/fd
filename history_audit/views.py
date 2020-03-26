# Create your views here.
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from reversion.models import Revision, Version
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.template import RequestContext
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db.models.fields import FieldDoesNotExist
from django.core.exceptions import ValidationError
import json


def history_home(request):
    return render(
        request,
        'history_audit/user_home.html',
    )

def user_list(request):
    user_rows = []
    for u in User.objects.all().order_by('id'):
        user_revisions = Revision.objects.filter(user=u)
        user_rows.append((u.pk, u.get_full_name(), user_revisions.count()))
        
    return render(
        request,
        'history_audit/user_list.html',
        {
            'user_rows': user_rows,
        },
    )
    
def user_info(request, user_id):
    title = "User History: " + User.objects.get(id = user_id).get_full_name()
    
    user = User.objects.get(id = user_id)
    revision_rows = []
    
    resultant_objects = Revision.objects.filter(user=user).order_by('-date_created')
    
    paginator = Paginator(resultant_objects, 50)
    page = int(request.GET.get('page', '1'))
    try:
        list_items = paginator.page(page)
    except (EmptyPage, InvalidPage):
        list_items = paginator.page(paginator.num_pages)
        
    for r in list_items.object_list:
        version_urls = []
        for v in r.version_set.all():
            try:
                object = v.content_type.model_class().objects.get(pk=v.object_id)
                url = reverse('admin:%s_%s_change' %(object._meta.app_label, object._meta.model_name), args=[object.id]) + 'history'
                version_urls.append((v, url))
            except:
                version_urls.append((v, 0))          
            
            
        revision_rows.append((r.date_created, version_urls, r.comment, r.id))
        #revision_rows.append((r.date_created, r.version_set.all(), r.comment))
    
    #for r in Revision.objects.filter(user = user).order_by('-date_created'):
    #    revision_rows.append((r.date_created, r.version_set.all(), r.comment))
    
    return render(
        request,
        'history_audit/user_history.html',
        {
            'title': title,
            'revision_rows': revision_rows,
            'list_items': list_items,
            'resultant_objs': resultant_objects,
        },
    )
    
def model_list(request):
    model_rows = []
    
    for c in ContentType.objects.all():
        model_revisions = Revision.objects.filter(version__content_type__id = c.id).distinct()
        model_rows.append((c.id, c.name.title(), model_revisions.count()))
        
        #model_rows_sorted = sorted(model_rows, key=revision_count: model_rows[2]), revision_count: model_rows[2])
    
    return render(
        request,
        'history_audit/model_list.html',
        {
            'model_rows': model_rows,
        },
    )
    
def model_info(request, type_id):
    title = "Model History: " + ContentType.objects.get(id = type_id).name.title()
    
    revision_rows = []
    
    resultant_objects = Revision.objects.filter(version__content_type__id = type_id).distinct().order_by('-date_created')
    
    paginator = Paginator(resultant_objects, 50)
    page = int(request.GET.get('page', '1'))
    try:
        list_items = paginator.page(page)
    except (EmptyPage, InvalidPage):
        list_items = paginator.page(paginator.num_pages)
        
    for r in list_items.object_list:
        version_urls = []
        for v in r.version_set.all():
            try:
                object = v.content_type.model_class().objects.get(pk=v.object_id)
                url = reverse('admin:%s_%s_change' %(object._meta.app_label, object._meta.model_name), args=[object.id]) + 'history'
                version_urls.append((v, url))
            except:
                version_urls.append((v, 0))  
        
        revision_rows.append((r.date_created, version_urls, r.comment, r.user, r.id))

    
    return render(
        request,
        'history_audit/model_history.html',
        {
            'title': title,
            'revision_rows': revision_rows,
            'list_items': list_items,
            'resultant_objs': resultant_objects,
        },
    )
        
def revision_info(request, revision_id, pagination_count = 5):


    pagination_count = int(pagination_count)
    
    if pagination_count > 5:
        show_all = 1
    else:
        show_all = 0
    
    revision = Revision.objects.get(id = revision_id)
    
    title = "Revision Details: Revision %s" % revision.id
    
    version_objects = revision.version_set.all()

    paginator = Paginator(version_objects, pagination_count)
    page = int(request.GET.get('page', '1'))
    try:
        list_items = paginator.page(page)
    except (EmptyPage, InvalidPage):
        list_items = paginator.page(paginator.num_pages)
    
    cached_version_objects = []   
    serialized_data = []
    for version_object in list_items.object_list:
        try:
            object = version_object.content_type.model_class().objects.get(pk=version_object.object_id)
            url = reverse('admin:%s_%s_change' %(object._meta.app_label, object._meta.model_name), args=[object.id]) + 'history'
        except:
            url = None
        
        try:        
            cached_version_objects.append((version_object, url, version_object.get_field_dict().iteritems(), 'current'))
        except (FieldDoesNotExist, ValidationError):
            data = json.loads(version_object.serialized_data)[0]
            cached_version_objects.append((version_object, url, data['fields'].iteritems(), 'serialized'))
        

    return render(
        request,
        'history_audit/revision_details.html',
        {
            'title': title,
            'show_all': show_all,
            'revision': revision,
            'list_items': list_items,
            'total_count': version_objects.count(),
            'resultant_objs':  version_objects,
            'version_objects': cached_version_objects,
        },
    )
    

def version_info(request, version_pk, redirect = False): #displays information about a single version object
    
    if redirect == 'True':
        title = "REDIRECTED FROM ADMIN PAGE: CANNOT REVERT TO THIS VERSION"
    else:    
        title = "Version Details: " + version_pk
    
    
    version_object = Version.objects.get(pk = version_pk)
 
    try:
        object = version_object.content_type.model_class().objects.get(pk=version_object.object_id)
        url = reverse('admin:%s_%s_change' %(object._meta.app_label, object._meta.model_name), args=[object.id]) + 'history'
    except:
        url = None
    
    try:        
        version_info = [version_object.get_field_dict().iteritems(), 'current']
    except (FieldDoesNotExist, ValidationError):
        data = json.loads(version_object.serialized_data)[0]
        version_info = [data['fields'].iteritems(), 'serialized'] 
    
    
    return render(
        request,
        'history_audit/version_details.html',
        {
            'title': title,
            'version_object': version_object,
            'url': url,
            'version_dict': version_info[0],
            'status': version_info[1],
        }
    )
    
    