from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProfilePage, name="home-page"),
    path('profile/', views.ProfilePage, name="profile-page"),
    path('login/', views.LoginPage, name="login-page"),
    path('',views.ProfilePage, name="profile-page"),
    path('login/',views.LoginPage, name="login-page"),
 	path('login-API/',views.ProfilePage, name="login-API"),
    path('signup/',views.ProfilePage, name="signup-page"),
 	path('signup-API/',views.ProfilePage, name="signup-API"),
 	# path('/user-profile',views.UserProfilePage, name="user-profile-page"),
 	path('user-profile-API/',views.ProfilePage, name="user-profile-API"),
]
