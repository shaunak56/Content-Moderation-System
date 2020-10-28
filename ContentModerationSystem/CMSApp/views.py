from django.shortcuts import render, HttpResponse
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required

from .models import *


def ProfilePage(request):

    try:
        context = {
            'user_obj': request.user,
            'tier_objs': Tier.objects.all(),
        }
        return render(request, 'CMSApp/profile.html', context)
    except Exception as e:
        print(str(e))
        return HttpResponse('Internal Error')


def LoginPage(request):

    try:
        context = {
            'tier_objs': Tier.objects.all(),
        }
        return render(request, 'CMSApp/login.html', context)
    except Exception as e:
        print(str(e))
        return HttpResponse('Internal Error')
