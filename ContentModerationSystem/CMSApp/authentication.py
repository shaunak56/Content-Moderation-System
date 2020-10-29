from django.contrib.auth.models import User
from rest_framework.authentication import BaseAuthentication,get_authorization_header

from rest_framework import exceptions
from ContentModerationSystem.settings import ACCESS_KEY_PREFIX
from django.contrib.auth import get_user_model
User = get_user_model()


class AccessKeyAuthentication(BaseAuthentication):

    def authenticate(self, request):
        credentials = get_authorization_header(request).split()


        if len(credentials)<2:
            raise exceptions.AuthenticationFailed('Credentials not provided')

        if len(credentials)>2:
            raise exceptions.AuthenticationFailed('Credential format not valid')

        credentials[0] = credentials[0].decode('utf-8')
        credentials[1] = credentials[1].decode('utf-8')

        if credentials[0]!=ACCESS_KEY_PREFIX:
            raise exceptions.AuthenticationFailed('Credential format not valid')

        access_key = credentials[1]

        try:
            user = User.objects.get(access_key=access_key)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('Access key invalid')

        return (user, None)
