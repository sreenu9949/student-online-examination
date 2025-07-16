# exam/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .models import Profile
from .forms import RegistrationForm
import pyotp
import qrcode
import io
import random

# ---------------------------
# Register View
# ---------------------------
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Hash password
            user.save()

            # Save profile with role
            role = form.cleaned_data['role']
            Profile.objects.create(user=user, role=role)

            login(request, user)
            return redirect('google_otp_setup')  # Your QR code view
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


# ---------------------------
# OTP Verification View
# ---------------------------
def verify_otp_view(request):
    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        stored_otp = request.session.get('otp')
        username = request.session.get('username')
        otp_type = request.session.get('otp_type')

        if otp_input == stored_otp and username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                messages.error(request, "User not found")
                return redirect('login')

            if otp_type == 'register':
                messages.success(request, "OTP verified. You can now login.")
                return redirect('login')
            elif otp_type == 'login':
                login(request, user)
                role = user.profile.role
                if role == 'student':
                    return redirect('student_dashboard')
                elif role == 'invigilator':
                    return redirect('invigilator_dashboard')
        else:
            messages.error(request, 'Invalid OTP')
            return redirect('verify_otp')

    return render(request, 'exam/verify_otp.html')


# ---------------------------
# Login View
# ---------------------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            otp = str(random.randint(100000, 999999))
            request.session['otp'] = otp
            request.session['username'] = username
            request.session['otp_type'] = 'login'

            send_mail(
                subject="Your Exam Portal OTP",
                message=f"Your OTP is: {otp}",
                from_email="youremail@example.com",
                recipient_list=[user.email],
                fail_silently=False,
            )

            messages.info(request, f"OTP sent to {user.email}")
            return redirect('verify_otp')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, "exam/login.html")


# ---------------------------
# OTP Login View (username only)
# ---------------------------
def otp_login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "User does not exist.")
            return redirect("otp_login")

        otp = str(random.randint(100000, 999999))
        request.session['otp'] = otp
        request.session['username'] = username
        request.session['otp_type'] = 'login'

        send_mail(
            subject="Your Exam Portal OTP",
            message=f"Your OTP is: {otp}",
            from_email="youremail@example.com",
            recipient_list=[user.email],
            fail_silently=False,
        )

        messages.info(request, f"OTP sent to {user.email}")
        return redirect('verify_otp')

    return render(request, "exam/otp_login.html")


# ---------------------------
# Dashboard Views
# ---------------------------
@login_required
def dashboard_view(request):
    return render(request, 'exam/dashboard.html')

@login_required
def student_dashboard_view(request):
    if request.user.profile.role != 'student':
        return redirect('login')
    return render(request, 'exam/student_dashboard.html')

@login_required
def invigilator_dashboard_view(request):
    if request.user.profile.role != 'invigilator':
        return redirect('login')
    return render(request, 'exam/invigilator_dashboard.html')


# ---------------------------
# Logout
# ---------------------------
def logout_view(request):
    logout(request)
    return redirect('login')
