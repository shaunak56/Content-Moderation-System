from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginPage, name="login-page"),
#    path('signup/', views.SignupPage, name="signup-page"),
    path('user-profile/', views.ProfilePage, name="profile-page"),
    path('usage-analysis', views.UsageAnalysisPage, name="usage-analysis-page"),
    path('billing/', views.Billing, name="billing-page"),

    path('signup-API/', views.SignupAPI.as_view(), name="signup-API"),
    path('login-API/', views.LoginAPI.as_view(), name="login-API"),
    path('user-profile-API/', views.UserProfileAPI.as_view(), name="user-profile-API"),
    path('usage-analysis-API/', views.UsageAnalysisAPI.as_view(), name="usage-analysis-API"),
    path('billing-API/', views.BillingAPI.as_view(), name="billing-API"),
    path('pay-bill-API/', views.PayBillAPI.as_view(), name="pay-bill-API"),

    path('content/', views.ContentAPI.as_view(), name="content_submit"),
    path('report/', views.RequestReportAPI.as_view(), name="request_report"),
    path('groups/', views.RequestContentGroupIdAPI.as_view(), name="group_list"),
]
