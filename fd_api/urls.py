# from django.urls import path
from django.conf.urls import url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth import views as auth_views
from fd_api import views
from rest_framework import routers
# Uncomment the next two lines to enable the admin:
from django.contrib import admin


router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'training', views.TrainingViewSet)
router.register(r'question', views.QuestionViewSet)
router.register(r'answer', views.AnswerViewSet)


urlpatterns = (
    url('', include(router.urls)),
    url('fd_api/', include('rest_framework.urls', namespace='rest_framework'))
)
