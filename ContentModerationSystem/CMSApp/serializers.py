from rest_framework.serializers import (ModelSerializer,StringRelatedField)
from .models import User

class UserProfileSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'access_key',
            'tier',
            'email',
            'is_active',
        )
        read_only_fields = [ "username", "access_key"]
