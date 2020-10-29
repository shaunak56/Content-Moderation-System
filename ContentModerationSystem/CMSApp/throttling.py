from rest_framework.throttling import UserRateThrottle
from rest_framework.authentication import (
    BaseAuthentication, get_authorization_header
)
from .models import User
from ContentModerationSystem import settings

class SubscriptionRateThrottle(UserRateThrottle):
    scope = "subscription"

    def __init__(self):
        super().__init__()

    def allow_request(self, request, view):

        if request.user.is_staff:
            # No throttling
            return True

        if request.user.is_active:
            user_daily_limit = request.user.tier.throttling_limit
            if user_daily_limit:
                # Override the default from settings.py
                self.duration = 3600
                self.num_requests = user_daily_limit
            else:
                # No limit == unlimited plan
                return True

        return super().allow_request(request=request,view=view)
