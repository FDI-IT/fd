# Create your views here.
from django.shortcuts import redirect, render_to_response
from django.contrib.auth import views as auth_views

def force_pwd_change(request, *args, **kwargs):
    response = auth_views.login(request, *args, **kwargs)
    if response.status_code == 302:
        if request.user.get_profile().force_password_change:
            return redirect('/django/accounts/password_change/')
    return response

def password_change(request,*args,**kwargs):
    response = auth_views.password_change(request,*args,**kwargs)
    if response.status_code == 302:
        up = request.user.get_profile()
        up.force_password_change = False
        up.save()
        return response
    return response
    