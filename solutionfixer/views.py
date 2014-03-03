# TODO add a confirmed field to a solution, and filter on those
# that are not confirmed

import re
from decimal import Decimal

from django.forms.models import modelformset_factory
from django.template import RequestContext
from django.utils import simplejson
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import permission_required
from django.db.models import Q

from access.models import Ingredient
from solutionfixer.models import Solution, SolutionStatus
from solutionfixer.parse_solutions import SolutionFixer
from solutionfixer import forms

def build_filter_kwargs(qdict, default):
    string_kwargs = {}
    for key in qdict.keys():
        if key == 'status':
            keyword = '%s__in' % (key)
            arg_list = []
            for my_arg in qdict.getlist(key):
                arg_list.append(my_arg)
            string_kwargs[keyword] = arg_list
    return string_kwargs

@permission_required('access.view_flavor')
def process_baserm_update(request):
    solution_id = request.POST['solution_id']
    baserm_id = request.POST['baserm_id']
    
    solution = Solution.objects.get(id=solution_id)
    try:
        solution.my_base = Ingredient.objects.get(id=baserm_id)
    except:
        solution.my_base = Ingredient.objects.filter(discontinued=False).get(id=baserm_id)
    solution.save()
    response_dict = {}
    return HttpResponse(simplejson.dumps(response_dict), content_type='application/json; charset=utf-8')

def ingredient_autocomplete(request):
    """
    This returns a JSON object that is an array of objects that have 
    the following properties: id, label, value. Labels are shown to
    the user in the form of a floating dialog. 
    """
    # this is provided by the jQuery UI widget
    term = request.GET['term']
        
    # todo:
    #
    # refactor the delegated functions so that only the ingredient
    # search is actually autocompleted...not the weight.
    # also refactor the 
    #
    # the search term has to be parsed, and scanned for a number.
    # if it has a number:
    #     and if it has an f: 
    #         search for flavor numbers.
    #     else:
    #         search for product numbers
    # else:
    #     search for product names
    match = re.search(r'[0-9]+', term)
    ret_array = []
    if match:
        if len(term) == 1:
            ingredients = Ingredient.objects.filter(id=int(term)).filter(discontinued=False)  
        else:
            ingredients = Ingredient.objects.filter(id__contains=match.group()).filter(discontinued=False)  
    else:
        ingredients = Ingredient.objects.filter(product_name__icontains=term)
    for ingredient in ingredients:
            ingredient_json = {}
            ingredient_json["id"] = ingredient.rawmaterialcode
            ingredient_json["label"] = ingredient.__unicode__()
            ingredient_json["value"] = ingredient_json["id"]
            ret_array.append(ingredient_json)
    return HttpResponse(simplejson.dumps(ret_array), content_type='application/json; charset=utf-8')


@permission_required('access.view_flavor')
def process_baserm_bypk_update(request):
    solution_id = request.POST['solution_id']
    baserm_id = request.POST['baserm_id']
    
    solution = Solution.objects.get(id=solution_id)
    solution.my_base = Ingredient.objects.get(rawmaterialcode=baserm_id)
    solution.save()
    response_dict = {}
    return HttpResponse(simplejson.dumps(response_dict), content_type='application/json; charset=utf-8')

@permission_required('access.view_flavor')
def process_solvent_update(request):
    solution_id = request.POST['solution_id']
    solution = Solution.objects.get(id=solution_id)
    
    try:
        solvent_id = request.POST['solvent_id']
        solution.my_solvent = Ingredient.objects.get(id=solvent_id)
    except:
        solution.my_solvent = None
    
    solution.save()
    response_dict = {}
    return HttpResponse(simplejson.dumps(response_dict), content_type='application/json; charset=utf-8')

@permission_required('access.view_flavor')
def process_percentage_update(request):
    solution_id = request.POST['solution_id']
    percentage = request.POST['percentage']
    solution = Solution.objects.get(id=solution_id)
    try:
        solution.percentage = Decimal(percentage)
        if solution.percentage < 0:
            solution.percentage = None
        solution.save()
        response_dict = {'percentage': str(solution.percentage)}
        return HttpResponse(simplejson.dumps(response_dict), content_type='application/json; charset=utf-8')
    except:
        solution.percentage = None
        solution.status=SolutionStatus.objects.get(id=1)
        solution.save()
        response_dict = {'validation_message': "Percentage must be a valid number"}
        return HttpResponse(simplejson.dumps(response_dict), content_type='application/json; charset=utf-8')

@permission_required('access.view_flavor')
def process_status_update(request):
    solution_id = request.POST['solution_id']
    status_id = request.POST['status_id']
    
    solution = Solution.objects.get(id=solution_id)
    status = SolutionStatus.objects.get(id=status_id)
    if status_id=='3':
        if (solution.my_base == None or
            solution.my_solvent == None or
            solution.percentage == None):
            solution.status=SolutionStatus.objects.get(id=1)
            response_dict = {'validation_message':"Can't verify solution unless all values are set"}
            return HttpResponse(simplejson.dumps(response_dict), content_type='application/json; charset=utf-8')
        
    solution.status=status
    solution.save()
    counts = {}
    counts['unverified'] = Solution.objects.filter(status__id=1).count()
    counts['flagged'] = Solution.objects.filter(status__id=2).count()
    counts['verified'] = Solution.objects.filter(status__id=3).count()
    counts['unlisted'] = Solution.objects.filter(status__id=4).count()
    response_dict = {'status_name':status.status_name,
                     'counts':counts}
    return HttpResponse(simplejson.dumps(response_dict), content_type='application/json; charset=utf-8')

@permission_required('solution.can_change')
def solution_review(request):
    page_title = "Solution Review"
    
    try:
        status_id = int(request.GET['status'])
    except:
        status_id = 1
        
    sol_status = SolutionStatus.objects.get(id=status_id)
    
    try:
        solution = Solution.objects.filter(status=sol_status)[0]
    except:
        return render_to_response('solutionfixer/no_unverified_remaining.html')

    
    if request.method == 'POST':
        solvent_form = forms.SolventForm(request.POST)
        percentage_form = forms.PercentageForm(request.POST)
        status_form = forms.SolutionStatusForm(request.POST)
        if solvent_form.is_valid() and percentage_form.is_valid() and status_form.is_valid():
            solution.my_solvent = Ingredient.objects.get(id=solvent_form.cleaned_data['solvent'])
            solution.percentage = percentage_form.cleaned_data['percentage']
            solution.my_base = Ingredient.objects.get(id=request.POST['base_ingredient'])
            solution.status = SolutionStatus.objects.get(id=status_form.cleaned_data['status'])
            solution.save()
            next_page = page+1
            return redirect('/django/solutionfixer/?page=%s' % next_page)

    try:
        solvent_form = forms.SolventForm(initial={'solvent': str(solution.my_solvent.id)})
    except:
        solvent_form = forms.SolventForm()
    try:
        percentage_form = forms.PercentageForm(initial={'percentage': solution.percentage})
    except:
        percentage_form = forms.PercentageForm()
    try:
        status_form = forms.SolutionStatusForm(initial={'status': solution.status.id})
    except:
        status_form = forms.SolutionStatusForm()
       
    sf = SolutionFixer() 
    matches = sf.get_related_ingredients(solution.ingredient)
    sorted_matches = []
    for key in sorted(matches.iterkeys(), reverse=True):
        sorted_matches.append((key, matches[key]))
    
    return render_to_response('solutionfixer/solution_review.html',
                              {
                               'solution':solution,
                               'matches':matches,
                               'sorted_matches':sorted_matches,
                               'solvent_form':solvent_form,
                               'percentage_form':percentage_form,
                               'status_form':status_form,
                               'page_title': page_title,
                               'get': request.GET,
                               },
                               context_instance=RequestContext(request))
    
@permission_required('solution.can_change')
def flagged_review(request):
    page_title = "Solution Review"
    
    try:
        status_id = int(request.GET['status'])
    except:
        status_id = 2
        
    sol_status = SolutionStatus.objects.get(id=status_id)
    
    try:
        solution = Solution.objects.filter(status=sol_status)[0]
    except:
        return render_to_response('solutionfixer/no_unverified_remaining.html')

    
    if request.method == 'POST':
        solvent_form = forms.SolventForm(request.POST)
        percentage_form = forms.PercentageForm(request.POST)
        status_form = forms.SolutionStatusForm(request.POST)
        if solvent_form.is_valid() and percentage_form.is_valid() and status_form.is_valid():
            solution.my_solvent = Ingredient.objects.get(id=solvent_form.cleaned_data['solvent'])
            solution.percentage = percentage_form.cleaned_data['percentage']
            solution.my_base = Ingredient.objects.get(id=request.POST['base_ingredient'])
            solution.status = SolutionStatus.objects.get(id=status_form.cleaned_data['status'])
            solution.save()
            next_page = page+1
            return redirect('/django/solutionfixer/?page=%s' % next_page)

    try:
        solvent_form = forms.SolventForm(initial={'solvent': str(solution.my_solvent.id)})
    except:
        solvent_form = forms.SolventForm()
    try:
        percentage_form = forms.PercentageForm(initial={'percentage': solution.percentage})
    except:
        percentage_form = forms.PercentageForm()
    try:
        status_form = forms.SolutionStatusForm(initial={'status': solution.status.id})
    except:
        status_form = forms.SolutionStatusForm()
       
    sf = SolutionFixer() 
    matches = sf.get_related_ingredients(solution.ingredient)
    sorted_matches = []
    for key in sorted(matches.iterkeys(), reverse=True):
        sorted_matches.append((key, matches[key]))
    
    return render_to_response('solutionfixer/solution_review.html',
                              {
                               'solution':solution,
                               'matches':matches,
                               'sorted_matches':sorted_matches,
                               'solvent_form':solvent_form,
                               'percentage_form':percentage_form,
                               'status_form':status_form,
                               'page_title': page_title,
                               'get': request.GET,
                               },
                               context_instance=RequestContext(request))
    
@permission_required('access.view_flavor')
def solution_summary(request, status=None):
    SolutionModelFormFormsetFactory = modelformset_factory(Solution,form=forms.SolutionModelForm, extra=0)
    if status == "unverified":
        filter_form = forms.SolutionFilterSelectForm()
        filter_form.fields['status'].initial = ('unverified',)
        show_filter_form=False
        
        solution_formset = SolutionModelFormFormsetFactory(queryset=Solution.objects.filter(status__id=1)[0:50])
    else:
        filter_form = forms.SolutionFilterSelectForm()
        my_queryset = Solution.objects.filter(Q(status__id=1) | Q(status__id=2) | Q(status__id=3))
        SolutionModelFormFormsetFactory = modelformset_factory(Solution,form=forms.SolutionModelForm, extra=0)    
        solution_formset = SolutionModelFormFormsetFactory(queryset=my_queryset[0:50])
        show_filter_form=True
    rendered_row_list = []
    for solution_form in solution_formset.forms:
        try:
            solution_form.fields['my_base_autocomplete'].initial = solution_form.instance.my_base
        except:
            pass
        try:
            solution_form.fields['solvent_choice'].initial = solution_form.instance.my_solvent.id
        except:
            pass
        rendered_row_list.append(solution_form.as_tr())
    rendered_rows = ''.join(rendered_row_list)
    context_dict = {'solution_formset': solution_formset,
                    'rendered_rows': rendered_rows,
                    'first_form': solution_formset.forms[0],
                    'mgmt_form':solution_formset.management_form,
                    'filter_form': filter_form,
                    'show_filter_form':show_filter_form,}
    return render_to_response('solutionfixer/solution_summary.html',
                              context_dict)
    
@permission_required('access.view_flavor')
def flagged_summary(request):
    SolutionModelFormFormsetFactory = modelformset_factory(Solution,form=forms.SolutionModelForm, extra=0)

    filter_form = forms.SolutionFilterSelectForm()
    
    solution_formset = SolutionModelFormFormsetFactory(queryset=Solution.objects.filter(status__id=2))

    rendered_row_list = []
    for solution_form in solution_formset.forms:
        try:
            solution_form.fields['my_base_autocomplete'].initial = solution_form.instance.my_base
        except:
            pass
        try:
            solution_form.fields['solvent_choice'].initial = solution_form.instance.my_solvent.id
        except:
            pass
        rendered_row_list.append(solution_form.as_tr())
    rendered_rows = ''.join(rendered_row_list)
    counts = {}
    counts['unverified'] = Solution.objects.filter(status__id=1).count()
    counts['flagged'] = Solution.objects.filter(status__id=2).count()
    counts['verified'] = Solution.objects.filter(status__id=3).count()
    counts['unlisted'] = Solution.objects.filter(status__id=4).count()
    context_dict = {'solution_formset': solution_formset,
                    'rendered_rows': rendered_rows,
                    'first_form': solution_formset.forms[0],
                    'mgmt_form':solution_formset.management_form,
                    'counts':counts}
    return render_to_response('solutionfixer/flagged_summary.html',
                              context_dict)
    

def solution_loader(request):
    """
    This returns a JSON object that is an array of objects that have 
    the following properties: id, label, value. Labels are shown to
    the user in the form of a floating dialog. 
    """
    # this is provided by the jQuery UI widget
    last_index = int(request.GET['last_index'][5:])
    show_statuses = {}
    if request.GET['show_unverified'] == u'true':
        show_statuses[1] = True
    if request.GET['show_flagged'] == u'true':
        show_statuses[2] = True
    if request.GET['show_verified'] == u'true':
        show_statuses[3] = True
    SolutionModelFormFormsetFactory = modelformset_factory(Solution,form=forms.SolutionModelForm, extra=0)    
    solution_formset = SolutionModelFormFormsetFactory(queryset=Solution.objects.all())
    
    solutions_to_show = []
    response_dict = {}
    rendered_rows = []
    i = last_index
    while len(solutions_to_show) < 25:
        i=i+1
        form = solution_formset.forms[i]
        try:
            form.fields['my_base_autocomplete'].initial = form.instance.my_base
        except:
            pass
        try:
            form.fields['solvent_choice'].initial = form.instance.my_solvent.id
        except:
            pass
        
        if form.instance.status_id in show_statuses:
            solutions_to_show.append(i)
            rendered_rows.append(form.as_tr(hidden=False))
        else:
            rendered_rows.append(form.as_tr(hidden=True))
    
    response_dict['new_last_index'] = i
    response_dict['visible_rows'] = solutions_to_show
    response_dict['rendered_rows'] = rendered_rows
    # get the queryset corresponding to the page num
    # pass it to a template that renders table rows to HTML
    # response_dict['hasNext'] = true or false
    # response_dict['rendered_rows'] = rendered rows
    return HttpResponse(simplejson.dumps(response_dict), content_type='application/json; charset=utf-8')

def post_match_guesses(request):
#    solution_ids = request.GET.getlist('solution_ids')
#    row_ids = request.GET.getlist('row_ids')

    solution_ids = request.POST.getlist('solution_ids')
    row_ids = request.POST.getlist('row_ids')
    sf = SolutionFixer()
    
    initial_sources = {} 
    for i in range(len(solution_ids)):
        solution = Solution.objects.get(id=solution_ids[i])
        matches = solution.solutionmatchcache_set.all()
        sorted_matches = []
        for m in matches:
            sorted_matches.append({
                'id': m.id,
                'value': m.value,
                'label':m.label,
            })
        initial_sources[row_ids[i]] = sorted_matches
    return_data = {'initial_sources': initial_sources}
    return HttpResponse(simplejson.dumps(return_data), content_type='application/json; charset=utf-8')

def solution_pin_review(request, ingredient_id):
    ingredients = Ingredient.objects.filter(id=ingredient_id)
    page_title = "Solution Review"
    table_headers = (
                     "Solution PIN",
                     "Base Raw Material",
                     "Solvent",
                     "Percentage",
                     "Status",
                     "Price",
    )
    highlighted_ingredient = ingredients[0]
    for ing in ingredients:
        if ing.discontinued == False:
            highlighted_ingredient = ing
            break
        
    related_solutions = []
    try:
        related_solutions.append(highlighted_ingredient.ing_obj)
    except:
        pass
    for sol in highlighted_ingredient.my_base.all():
        related_solutions.append(sol)
    for sol in highlighted_ingredient.my_solvent.all():
        related_solutions.append(sol)
        
    context_dict = {
        'highlighted_ingredient': highlighted_ingredient,
        'related_solutions': related_solutions,
        'page_title': page_title,
        'table_headers': table_headers,
    }
    return render_to_response('solutionfixer/solution_pin_review.html',
                              context_dict)
    