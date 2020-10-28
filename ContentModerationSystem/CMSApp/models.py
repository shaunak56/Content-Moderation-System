from django.db import models
from django.contrib.auth.models import AbstractUser
from .constants import *

import uuid

# class UserManager(models.Manager):
#     def get_queryset(self):
#         return super().get_queryset().filter(is_deleted=False)


class TierManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class User(AbstractUser):

    access_key = models.CharField(max_length=200)
    account_id = models.CharField(max_length=200)
    tier = models.ForeignKey('Tier', blank=True, null=True, on_delete=models.SET_NULL)
    is_deleted = models.BooleanField(default=False)
    # objects = UserManager
    # admin_objects = models.Manager

    def __str__(self):
        if self.first_name:
            return self.first_name+" "+self.last_name
        return self.username


class Tier(models.Model):

    name = models.CharField(max_length=200, blank=False, null=False)
    price = models.FloatField(default=0.0)
    price_unit = models.CharField(max_length=200, choices=CURRENCY_UNITS, blank=False, null=False)
    throttling_limit = models.IntegerField(default=0)
    content_size = models.IntegerField(default=0)

    is_deleted = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)

    objects = TierManager
    admin_objects = models.Manager

    def __str__(self):
        return self.name


# class ThrottleLimit(models.Model):
#
#     tier = models.ForeignKey('Tier', blank=False, null=False, on_delete=models.CASCADE)


class Content(models.Model):

    text = models.TextField(blank=True, null=True)
    content_group = models.ForeignKey('ContentGroup', blank=True, null=True, on_delete=models.SET_NULL)
    created_on = models.DateTimeField(auto_now_add=True)


class ContentGroup(models.Model):

    user = models.ForeignKey('User', blank=True, null=True, on_delete=models.SET_NULL)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    report_status = models.CharField(max_length=200, choices=REPORT_STATUS_CHOICES)
    created_on = models.DateTimeField(auto_now_add=True)


class Report(models.Model):

    report = models.TextField(default={}, blank=True, null=True)
    content = models.ForeignKey('Content', blank=True, null=True, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
