# Create your views here.
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views

def force_pwd_change(request, *args, **kwargs):
    response = auth_views.login(request, *args, **kwargs)
    if response.status_code == 302:
        if request.user.userprofile.force_password_change:
            return redirect('/accounts/password_change/')
    return response

def password_change(request,*args,**kwargs):
    response = auth_views.password_change(request,*args,**kwargs)
    if response.status_code == 302:
        up = request.user.userprofile
        up.force_password_change = False
        up.save()
        return response
    return response
