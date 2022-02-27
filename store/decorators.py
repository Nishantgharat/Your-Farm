from django.http import HttpResponse
from django.shortcuts import redirect
from .models import User


def unauthenticated_user(view_fun):
    def wrapper_fun(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        else:
            return view_fun(request, *args, **kwargs)
    return wrapper_fun


def allowed_users(allowed_rolls=[]):
    def decorator(view_fun):
        def wrapper_fun(request, *args, **kwargs):

            print('user type',request.user.user_type)

            if request.user.user_type in allowed_rolls :
                return view_fun(request, *args, **kwargs)
            else:
                return redirect('index')      
        return wrapper_fun
    return decorator