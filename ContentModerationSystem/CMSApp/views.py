from django.shortcuts import render, HttpResponse
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import login_required

from .models import *


def ProfilePage(request):

    try:
        context = {}
        return render(request, 'CMSApp/profile.html', context)
    except Exception as e:
        print(str(e))
        return HttpResponse('Internal Error')
