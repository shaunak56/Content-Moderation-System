from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProfilePage, name="profile-page"),
]
