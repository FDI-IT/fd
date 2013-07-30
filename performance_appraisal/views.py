import string

from django.shortcuts import render_to_response, get_object_or_404

from performance_appraisal.models import PerformanceAppraisal

def get_help_text(field_name):
    return PerformanceAppraisal._meta.get_field(field_name).help_text

def get_areacell_contents(field_name):
    return "<b>%s</b> - %s" % (string.replace(string.capitalize(field_name[:-9]), '_', ' '), get_help_text(field_name))


def appraisal_review(request, appraisal_id):
    appraisal = get_object_or_404(PerformanceAppraisal, pk=appraisal_id)
    rating_choices = list(PerformanceAppraisal.RATING_CHOICES)
    rating_choices.reverse()
    
    appraisal_list = (
        ('quality_comments','quality_rating'),
        ('productivity_comments','productivity_rating'),
        ('job_knowledge_comments','job_knowledge_rating'),
        ('reliability_comments','reliability_rating'),
        ('attendance_comments','attendance_rating'),
        ('creativity_comments','creativity_rating'),
        ('initiative_comments','initiative_rating'),
        ('adherence_to_policy_comments','adherence_to_policy_rating'),
        ('interpersonal_relationships_comments','interpersonal_relationships_rating'),
        ('judgement_comments','judgement_rating'),
    )
    appraisal_table = []
    for comments, rating in appraisal_list:
        areacell = get_areacell_contents(comments)
        ratingcell = appraisal.__getattribute__(rating)
        commentscell = appraisal.__getattribute__(comments)
        
        appraisal_table.append((areacell,ratingcell,commentscell,))
    
    
    return render_to_response('performance_appraisal/appraisal_review.html',
                              {
                               'appraisal': appraisal,
                               'rating_choices':rating_choices,
                               'appraisal_table':appraisal_table,
                               'PerformanceAppraisal':PerformanceAppraisal,
                               })