from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from django.contrib.auth.admin import UserAdmin

from .models import Tier
from django.core.exceptions import ObjectDoesNotExist

import threading
from .utils import moderate

app_models = apps.get_app_config('CMSApp').get_models()

class CustomUserAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('access_key','tier')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('access_key','tier')}),
    )


for model in app_models:
    try:
        if str(model) == "<class 'CMSApp.models.User'>":
            admin.site.register(model,CustomUserAdmin)
        else:
            admin.site.register(model)
    except AlreadyRegistered:
        pass

generate_result_task = threading.Thread(target=moderate)
generate_result_task.daemon = True
generate_result_task.start()

try:
    tier = Tier.objects.get(name='Free')
except ObjectDoesNotExist:
    try:
        Tier.objects.create(name='Free',throttling_limit=5,content_size=100)
    except:
        pass
except:
    pass
