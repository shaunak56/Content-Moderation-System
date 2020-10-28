from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, \
	BasicAuthentication
from rest_framework.views import APIView
from CMSApp.models import *

from ContentModerationSystem import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


from django.http import HttpResponse, HttpResponseRedirect,HttpResponseNotFound

import json
import uuid
from datetime import datetime,time,date,timedelta
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

	return render(request,'CMSApp/login.html',context)

def SignupPage(request):
	return render(request,'CMSApp/login.html')

@login_required
def ProfilePage(request):
	return render(request,'CMSApp/profile.html')

# LOGGER

def error():
	exc_type, exc_value, exc_traceback = sys.exc_info()
	print("\nLINE = :", exc_traceback.tb_lineno)
	formatted_lines = traceback.format_exc().splitlines()
	print("ERROR = ", formatted_lines[-1],end="\n")

# API SECTION BELOW

class LoginAPI(APIView):

	authentication_classes = (BasicAuthentication)

	def post(self, request, *args, **kwargs):

		response = {}
		response["status"] = 500

		try:
			data = request.data

			user = authenticate(username=data['username'], password=data['password'])

			if(user is not None):
				response['status'] = 200
				login(request, user)
			else:
				response['status'] = 401

		except Exception as e:
			error()
			print("ERROR IN LoginAPI", str(e))

		return Response(data=response)


class SignupAPI(APIView):

	authentication_classes = (BasicAuthentication)

	def post(self, request, *args, **kwargs):
		response = {}
		response["status"] = 500

		try:
			data = request.data

			tier_pk = data["tier_pk"]
			first_name = data["first_name"]
			last_name = data["last_name"]
			username = data["username"]
			password = data["password"]
			email = data["email"]

			if(User.objects.filter(username=username).exist()):
				response['status']  = 409
			else:
				try:
					tier = Tier.objects.get(pk=tier_pk)

					user = User.objects.create(

						username=username,
						email=email,
						password=password,
						tier=tier,
						first_name=first_name,
						last_name=last_name
					)
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
	permission_classes = [IsAuthenticated,]

	def get(self, request, *args, **kwargs):
		response = {}
		try:
			data = request.data
			user = request.user
			response["data"] = UserProfileSerializer(user,context={'request':request}).data
		except Exception as e:
			print("ERROR IN = Validate_TokenAPI", str(e))
			return Response(data=response,status = HTTP_401_UNAUTHORIZED)

		return Response(data=response,status = HTTP_200_OK)

	def patch(self, request, *args, **kwargs):
		response = {}

		try:
			data = request.data
			user = request.user
			serializer = UserProfileSerializer(user, data=request.data, partial=True,context={'request':request}) # set partial=True to update a data partially
			if serializer.is_valid():
				serializer.save()
			else:
				response["details"]=serializer.errors
				return Response(data=response,status = HTTP_409_CONFLICT)
		except Exception as e:
			print("ERROR IN = Validate_TokenAPI", str(e))
			return Response(data=response,status = HTTP_401_UNAUTHORIZED)

		return Response(data=response)
