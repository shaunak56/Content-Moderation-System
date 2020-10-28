from django.urls import path
from . import views

urlpatterns = [
    path('login/',views.LoginPage, name="login-page"),
 	path('login-API/',views.LoginAPI.as_view(), name="login-API"),
    path('signup/',views.SignupPage, name="signup-page"),
 	path('signup-API/',views.SignupAPI.as_view(), name="signup-API"),
    path('user-profile/',views.ProfilePage, name="profile-page"),
 	path('user-profile-API/',views.UserProfileAPI.as_view(), name="user-profile-API"),
]
