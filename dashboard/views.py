from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.


@login_required(login_url="login")
def dashboard(request):
    # messages.error(request, request.user.user_type, extra_tags='success')
    return render(request, "dashboard/index.html")
