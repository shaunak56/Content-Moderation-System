from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, \
    BasicAuthentication
from rest_framework.views import APIView
from django.utils import timezone

from CMSApp.models import *
from .constants import *

from ContentModerationSystem import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound

import json
import uuid
from datetime import datetime, time, date, timedelta
from calendar import monthrange

from django.utils.timezone import localtime

from .serializers import UserProfileSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.status import (HTTP_200_OK,
                                   HTTP_202_ACCEPTED,
                                   HTTP_208_ALREADY_REPORTED,
                                   HTTP_400_BAD_REQUEST,
                                   HTTP_412_PRECONDITION_FAILED,
                                   HTTP_409_CONFLICT,
                                   HTTP_401_UNAUTHORIZED,
                                   HTTP_404_NOT_FOUND)

import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
import traceback


# 400 Bad Request
# 401 Unauthorized
# 403 Forbidden
# 404 Not Found
# 409 Conflict
# 200 OK
# 201 Created
# 202 Accepted

# CLASSES BELOW

def LoginPage(request):
    context = {}
    context["tier_objs"] = Tier.objects.all()

    return render(request, 'CMSApp/login.html', context)


def SignupPage(request):
    context = {}
    context["tier_objs"] = Tier.objects.all()

    return render(request, 'CMSApp/login.html')


@login_required(login_url='/login/')
def ProfilePage(request):
    context = {
        'user_obj': request.user,
        'tier_objs': Tier.objects.all()
    }
    return render(request, 'CMSApp/profile.html', context)


@login_required(login_url='/login/')
def UsageAnalysisPage(request):
    return render(request, 'CMSApp/usage-analysis.html')


# LOGGER

def error():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    print("\nLINE = :", exc_traceback.tb_lineno)
    formatted_lines = traceback.format_exc().splitlines()
    print("ERROR = ", formatted_lines[-1], end="\n")


# API SECTION BELOW

class LoginAPI(APIView):
    authentication_classes = (BasicAuthentication,)

    def post(self, request, *args, **kwargs):

        response = {}
        response["status"] = 500

        try:
            data = request.data

            user = authenticate(username=data['username'], password=data['password'])
            print(user, data)
            if (user is not None):
                response['status'] = 200
                login(request, user)
            else:
                response['status'] = 401

        except Exception as e:
            error()
            print("ERROR IN LoginAPI", str(e))

        return Response(data=response)


class SignupAPI(APIView):
    authentication_classes = (BasicAuthentication,)

    def post(self, request, *args, **kwargs):
        response = {}
        response["status"] = 500

        try:
            data = request.data
            print(data)
            tier_pk = data["tier_pk"]
            first_name = data["first_name"]
            last_name = data["last_name"]
            username = data["username"]
            password = data["password"]
            email = data["email"]

            if (User.objects.filter(username=username).exists()):
                response['status'] = 409
            else:
                try:
                    tier = Tier.objects.get(pk=tier_pk)

                    user = User.objects.create(
                        username=username,
                        email=email,
                        tier=tier,
                        first_name=first_name,
                        last_name=last_name)
                    user.set_password(password)
                    user.save()
                    response['status'] = 202

                except Exception as e:
                    error()
                    response['status'] = 400

        except Exception as e:
            error()
            print("ERROR IN SignupAPI", str(e))

        return Response(data=response)


class UserProfileAPI(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        response = {}
        try:
            data = request.data
            user = request.user
            response["data"] = UserProfileSerializer(user, context={'request': request}).data
        except Exception as e:
            error()
            print("ERROR IN = Validate_TokenAPI", str(e))
            return Response(data=response, status=HTTP_401_UNAUTHORIZED)

        return Response(data=response, status=HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        response = {}

        try:
            data = request.data
            user = request.user
            serializer = UserProfileSerializer(user, data=request.data, partial=True, context={
                'request': request})  # set partial=True to update a data partially
            if serializer.is_valid():
                serializer.save()
            else:
                response["details"] = serializer.errors
                return Response(data=response, status=HTTP_409_CONFLICT)
        except Exception as e:
            error()
            print("ERROR IN = Validate_TokenAPI", str(e))
            return Response(data=response, status=HTTP_401_UNAUTHORIZED)

        return Response(data=response, status=HTTP_200_OK)


def UsageAnalysisPage(request):
    start_time = ""
    end_time = ""

    try:
        start_date = datetime.strptime(request.GET['start_date'], "%d-%m-%Y-%H-%M")
    except:
        start_date = ""

    try:
        end_date = datetime.strptime(request.GET['end_date'], "%d-%m-%Y-%H-%M")
    except:
        end_date = ""

    context = {
        'start_date': start_date,
        'end_date': end_date,
        'start_time': start_time,
        'end_time': end_time
    }

    return render(request, 'CMSApp/usage_analysis.html', context)


class UsageAnalysisAPI(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        response = {}
        try:
            data = request.data
            user = request.user
            print(request.GET)
            request.GET.get('start_date', '-1')
            request.GET.get('end_date', '-1')

            content_group_objects = ContentGroup.objects.none()

            start_date_time = None
            end_date_time = None

            try:
                start_date_time = datetime.strptime(request.GET['start_date'] + "-" + request.GET['start_time'],
                                                    "%d/%m/%Y-%H:%M")-timedelta(hours=5, minutes=30)
            except:
                pass

            try:
                end_date_time = datetime.strptime(request.GET['end_date'] + "-" + request.GET['end_time'],
                                                  "%d/%m/%Y-%H:%M")-timedelta(hours=5, minutes=30)
            except:
                pass
            print(start_date_time, end_date_time)
            try:
                content_group_objects = ContentGroup.objects.filter(user=user)

                if start_date_time is None and end_date_time is None:
                    content_group_objects = content_group_objects.filter(
                        created_on__gte=timezone.now() - timedelta(hours=1))
                else:
                    try:
                        content_group_objects = content_group_objects.filter(created_on__gte=start_date_time)
                    except:
                        pass
                    try:
                        content_group_objects = content_group_objects.filter(created_on__lte=end_date_time)
                    except:
                        pass
            except:
                content_group_objects = None

            response["content_group_objects"] = []

            for content_group_object in content_group_objects:
                temp = {"created_on": (content_group_object.created_on+timedelta(hours=5, minutes=30)).strftime("%d-%m-%Y %H:%M"), "uuid": content_group_object.uuid,
                        "status": report_status_choices_dict[content_group_object.report_status],
                        "entries": content_group_object.content_set.count()}

                response["content_group_objects"].append(temp)

        except Exception as e:
            error()
            print("ERROR IN UsageAnalysisAPI", str(e))
            return Response(data=response, status=HTTP_401_UNAUTHORIZED)

        return Response(data=response, status=HTTP_200_OK)
