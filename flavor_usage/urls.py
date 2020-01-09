from django.conf.urls import url, include
from flavor_usage import views

urlpatterns = (
    url(r'^(?P<flavor_number>\d+)/new_usage/$', views.new_usage),
    url(r'^test/$', views.test),
)
