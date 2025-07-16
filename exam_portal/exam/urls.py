"""
URL configuration for exam_portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# exam/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_redirect, name='home_redirect'),
    path('register/', views.register_view, name='register'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('google-otp-setup/', views.google_otp_setup, name='google_otp_setup'),
    path('login/', views.login_view, name='login'),
    path('google-otp-verify/', views.google_otp_verify, name='google_otp_verify'),
    path('otp-login/', views.otp_login_view, name='otp_login'),
    path('student-dashboard/', views.student_dashboard_view, name='student_dashboard'),
    path('invigilator-dashboard/', views.invigilator_dashboard_view, name='invigilator_dashboard'),
    path('logout/', views.logout_view, name='logout'),
]

