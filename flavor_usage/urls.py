from django.conf.urls.defaults import *

urlpatterns = patterns('flavor_usage.views',
    (r'^(?P<flavor_number>\d+)/new_usage/$', 'new_usage'),
)
