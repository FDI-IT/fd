from django.db import models

# Create your models here.

class Department(models.Model):
    name = models.CharField(max_length=40)
    
    def __unicode__(self):
        return self.name

class PerformanceAppraisal(models.Model):
    RATING_CHOICES = (
        (1, 'Unsatisfactory'),
        (2, 'Improvement Needed'),
        (3, 'Adequate'),
        (4, 'Good'),
        (5, 'Very Good'),
        (6, 'Excellent'),
    )
    
    REASON_CHOICES = (
        ('Annual', 'Annual'),
        ('Promotion', 'Promotion'),
        ('Unsatisfactory performance', 'Unsatisfactory performance'),
        ('Other', 'Other'),                 
    )
    
    employee_name = models.CharField(max_length=40)
    department = models.ForeignKey('Department')
    title = models.CharField(max_length=40)
    reason_for_review = models.CharField(max_length=40, choices=REASON_CHOICES)
    period_start = models.DateField()
    period_end = models.DateField()
    
    quality_rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    quality_comments = models.TextField(help_text="Accuracy, thoroughness, neatness. Observes prescribed breaks and good overall attendance.", blank=True)
    productivity_rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    productivity_comments = models.TextField(help_text="Production of significant amount of work, and efficiency in a given time.", blank=True)
    job_knowledge_rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    job_knowledge_comments = models.TextField(help_text="Possession of practical and technical knowledge.", blank=True)
    reliability_rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    reliability_comments = models.TextField(help_text="Reliance for task completion and follow-up.", blank=True)
    attendance_rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    attendance_comments = models.TextField(help_text="Punctual?", blank=True)
    creativity_rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    creativity_comments = models.TextField(help_text="Proposes ideas and finds new and better ways to do things.", blank=True)
    initiative_rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    initiative_comments = models.TextField(help_text="Seeks out new assignments and assumes additional duties.", blank=True)
    adherence_to_policy_rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    adherence_to_policy_comments = models.TextField(help_text="Follows Safety and Conduct rules, regulations and company policies.", blank=True)
    interpersonal_relationships_rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    interpersonal_relationships_comments = models.TextField(help_text="Ability to cooperate, work and communicate with coworkers, supervisors, and subordinates, as well as outside contractors, etc.", blank=True)
    judgement_rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    judgement_comments = models.TextField(help_text="Proper judgement and decision making skills.", blank=True)
    
    additional_comments = models.TextField(blank=True)
    
    def get_score(self):
        return (self.quality_rating +
                 self.productivity_rating +
                 self.job_knowledge_rating +
                 self.reliability_rating +
                 self.attendance_rating +
                 self.creativity_rating +
                 self.initiative_rating +
                 self.adherence_to_policy_rating +
                 self.interpersonal_relationships_rating +
                 self.judgement_rating
                 )
        
    def get_grade(self, score=None):
        if not score:
            score = self.get_score()
        if score < 22:
            grade = "Unsatisfactory"
        elif score < 33:
            grade = "Improvement Needed"
        elif score < 44:
            grade = "Adequate"
        elif score < 55:
            grade = "Good"
        elif score < 66:
            grade = "Very Good"
        else:
            grade = "Excellent"
        return grade
    
    def __unicode__(self):
        score = self.get_score()
        grade = self.get_grade(score)
        return "%s - %s to %s - Score: %s - %s" % (self.employee_name, self.period_start, self.period_end, score, grade)
