from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_redirect, name='home'),
    path('register/', views.register_view, name='register'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('login/', views.login_view, name='login'),
    path('otp-login/', views.otp_login_view, name='otp_login'),
    path('logout/', views.logout_view, name='logout'),
    path('google-otp-setup/', views.google_otp_setup, name='google_otp_setup'),
    path('google-otp-verify/', views.google_otp_verify, name='google_otp_verify'),
    path('student-dashboard/', views.student_dashboard_view, name='student_dashboard'),
    path('invigilator-dashboard/', views.invigilator_dashboard_view, name='invigilator_dashboard'),
]
