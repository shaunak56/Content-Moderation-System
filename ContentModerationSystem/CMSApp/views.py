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
                                   HTTP_404_NOT_FOUND,
                                   HTTP_403_FORBIDDEN)

from .throttling import SubscriptionRateThrottle
from .authentication import AccessKeyAuthentication

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


@login_required(login_url='/cms/login/')
def ProfilePage(request):
    context = {
        'user_obj': request.user,
        'tier_objs': Tier.objects.all()
    }
    return render(request, 'CMSApp/profile.html', context)


@login_required(login_url='/cms/login/')
def Logout(request):
    logout(request)
    return HttpResponseRedirect('/cms/login/')


@login_required(login_url='/cms/login/')
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
    # authentication_classes = [AccessKeyAuthentication]
    # throttle_classes = [SubscriptionRateThrottle]
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        response = {}
        try:
            data = request.data
            user = request.user
            print('api user : ' + str(user))
            print(request.GET)
            request.GET.get('start_date', '-1')
            request.GET.get('end_date', '-1')

            content_group_objects = ContentGroup.objects.none()

            start_date_time = None
            end_date_time = None

            try:
                start_date_time = datetime.strptime(request.GET['start_date'] + "-" + request.GET['start_time'],
                                                    "%d/%m/%Y-%H:%M") - timedelta(hours=5, minutes=30)
            except:
                pass

            try:
                end_date_time = datetime.strptime(request.GET['end_date'] + "-" + request.GET['end_time'],
                                                  "%d/%m/%Y-%H:%M") - timedelta(hours=5, minutes=30)
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
                temp = {"created_on": (content_group_object.created_on + timedelta(hours=5, minutes=30)).strftime(
                    "%d-%m-%Y %H:%M"), "uuid": content_group_object.uuid,
                    "status": report_status_choices_dict[content_group_object.report_status],
                    "entries": content_group_object.content_set.count()}

                response["content_group_objects"].append(temp)

        except Exception as e:
            error()
            print("ERROR IN UsageAnalysisAPI", str(e))
            return Response(data=response, status=HTTP_401_UNAUTHORIZED)

        return Response(data=response, status=HTTP_200_OK)


def Billing(request):
    try:
        start_date = datetime.strptime(request.GET['start_date'], "%d-%m-%Y")
    except:
        start_date = ""

    try:
        end_date = datetime.strptime(request.GET['end_date'], "%d-%m-%Y")
    except:
        end_date = ""

    context = {
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'CMSApp/billing.html', context)


class BillingAPI(APIView):
    # authentication_classes = [AccessKeyAuthentication]
    # throttle_classes = [SubscriptionRateThrottle]
    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        response = {}
        try:
            data = request.data
            user = request.user

            start_date_time = None
            end_date_time = None

            try:
                start_date_time = datetime.strptime(request.GET['start_date'], "%d/%m/%Y") - timedelta(hours=5,
                                                                                                       minutes=30)
            except:
                pass

            try:
                end_date_time = datetime.strptime(request.GET['end_date'], "%d/%m/%Y") - timedelta(hours=5, minutes=30)
            except:
                pass
            try:
                bill_entries = MonthlyBill.objects.filter(user=user)

                if start_date_time is None and end_date_time is None:
                    bill_entries = bill_entries.filter(
                        created_on__gte=timezone.now() - timedelta(days=180))
                else:
                    try:
                        bill_entries = bill_entries.filter(created_on__gte=start_date_time)
                    except:
                        pass
                    try:
                        bill_entries = bill_entries.filter(created_on__lte=end_date_time)
                    except:
                        pass
            except Exception as e:
                print(str(e))
                bill_entries = []

            response["bill_objects"] = []

            for bill_entry in bill_entries:
                temp = {"bill_no": bill_entry.pk,
                        "created_on": (bill_entry.created_on + timedelta(hours=5, minutes=30)).strftime("%d-%m-%Y"),
                        "status": bill_entry.is_paid,
                        "bill_unit": bill_entry.price_unit,
                        "bill_amount": str(bill_entry.price)}

                response["bill_objects"].append(temp)
        except Exception as e:
            error()
            print("ERROR IN BillingAPI", str(e))
            return Response(data=response, status=HTTP_401_UNAUTHORIZED)

        return Response(data=response, status=HTTP_200_OK)


class PayBillAPI(APIView):
    # authentication_classes = [AccessKeyAuthentication]
    # throttle_classes = [SubscriptionRateThrottle]
    permission_classes = [IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        response = {}
        try:
            data = request.data
            user = request.user

            bill_obj = MonthlyBill.objects.get(pk=int(data['bill_no']))

            if bill_obj.user != user:
                raise Exception("Unauthorised access")

            if bill_obj.created_on.month == timezone.now().month and bill_obj.created_on.year == timezone.now().year:
                return Response(data=response, status=HTTP_403_FORBIDDEN)

            bill_obj.is_paid = True
            bill_obj.save()

        except Exception as e:
            error()
            print("ERROR IN PaybillAPI", str(e))
            return Response(data=response, status=HTTP_401_UNAUTHORIZED)

        return Response(data=response, status=HTTP_200_OK)


class ContentAPI(APIView):
    authentication_classes = [AccessKeyAuthentication]
    throttle_classes = [SubscriptionRateThrottle]

    def post(self, request, *args, **kwargs):
        response = {}
        try:
            data = request.data
            user = request.user

            list = data['comments']

            if len(list) > user.tier.content_size or len(list) == 0:
                response['details'] = 'You cannot send more than ' + str(
                    user.tier.content_size) + ' and less than  1 comments in one API call in this tier'
                return Response(data=response, status=HTTP_400_BAD_REQUEST)

            comment_ids = []
            comment_texts = []
            for comment in list:
                comment_ids.append(comment['id'])
                comment_texts.append(comment['text'])

            group = ContentGroup.objects.create(user=user)

            for i in range(len(comment_ids) - 1):
                Content.objects.create(text_id=comment_ids[i], text=comment_texts[i], content_group=group)

            index = len(comment_ids) - 1
            Content.objects.create(text_id=comment_ids[index], text=comment_texts[index], content_group=group,
                                   is_last=True)
            response['details'] = 'Comments added to the juding queue. Please find you report soon using the group_id'
            response['group_id'] = str(group.uuid)

            current_month_bill = MonthlyBill.objects.filter(user=user, created_on__month=timezone.now().month).filter(created_on__year=timezone.now().year)
            if current_month_bill.count() == 0:
                if user.tier is None:
                    user.tier = Tier.objects.get(name='Free')
                    user.save()
                MonthlyBill.objects.create(user=user, created_on=timezone.now(), price=user.tier.price, price_unit=user.tier.price_unit)

            return Response(data=response, status=HTTP_202_ACCEPTED)
        except Exception as e:
            response['details'] = str(e)
            return Response(data=response, status=HTTP_400_BAD_REQUEST)


class RequestReportAPI(APIView):
    authentication_classes = [AccessKeyAuthentication]

    def post(self, request, *args, **kwargs):
        response = {}
        try:
            data = request.data
            user = request.user

            id = data['group_id']
            group = ContentGroup.objects.get(uuid=id)
            response['status'] = group.report_status
            if group.report_status == '1':
                reports = []
                reports_objs = Report.objects.filter(content__content_group=group)
                for reports_obj in reports_objs:
                    reports.append(json.loads(reports_obj.report))
                response['reports'] = reports
            return Response(data=response, status=HTTP_202_ACCEPTED)
        except Exception as e:
            response['details'] = str(e)
            return Response(data=response, status=HTTP_400_BAD_REQUEST)


class RequestContentGroupIdAPI(APIView):
    authentication_classes = [AccessKeyAuthentication]

    def post(self, request, *args, **kwargs):
        response = {}
        try:
            data = request.data
            user = request.user

            start_time = data['start_time']
            end_time = data['end_time']

            start_date_time = datetime.strptime(start_time, "%d/%m/%Y-%H:%M") - timedelta(hours=5, minutes=30)
            end_date_time = datetime.strptime(end_time, "%d/%m/%Y-%H:%M") - timedelta(hours=5, minutes=30)

            groups = ContentGroup.objects.filter(created_on__lte=end_date_time, created_on__gte=start_date_time,
                                                 user=request.user)

            list_data = []

            for group in groups:
                data_dic = {}
                data_dic['uuid'] = group.uuid
                data_dic['submitted_on'] = datetime.strftime(group.created_on + timedelta(hours=5, minutes=30),
                                                             "%d/%m/%Y-%H:%M")
                data_dic['status'] = group.report_status
                list_data.append(data_dic)

            response['groups'] = list_data

            return Response(data=response, status=HTTP_200_OK)
        except Exception as e:
            response['details'] = str(e)
            return Response(data=response, status=HTTP_400_BAD_REQUEST)
