from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from .models import Profile
import random

# ---------------------------
# Register View
# ---------------------------
def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        role = request.POST.get('role')

        # 1. Validation
        if not all([username, email, password1, password2, role]):
            messages.error(request, "All fields are required.")
            return redirect('register')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use.")
            return redirect('register')

        # 2. Create user
        user = User.objects.create_user(username=username, email=email, password=password1)

        # 3. Create Profile safely
        try:
            Profile.objects.create(user=user, role=role)
        except Exception as e:
            user.delete()  # Rollback user creation if profile fails
            messages.error(request, f"Failed to create profile: {str(e)}")
            return redirect('register')

        messages.success(request, "Account created successfully. You can now log in.")
        return redirect('login')

    return render(request, 'exam/register.html')



# ---------------------------
# OTP Verification View
# ---------------------------
def verify_otp_view(request):
    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        stored_otp = request.session.get('otp')
        username = request.session.get('username')
        otp_type = request.session.get('otp_type')

        if otp_input == stored_otp:
            if otp_type == 'register':
                # ✅ Registration success, redirect to login
                messages.success(request, "OTP verified. You can now login.")
                return redirect('login')
            elif otp_type == 'login':
                # ✅ OTP login, now authenticate
                user = User.objects.get(username=username)
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
# Login View (username/password)
# ---------------------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            role = user.profile.role
            if role == 'student':
                return redirect('student_dashboard')
            elif role == 'invigilator':
                return redirect('invigilator_dashboard')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, "exam/login.html")


# ---------------------------
# OTP Login View
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
            from_email="youremail@example.com",  # ✅ Make sure email config is correct
            recipient_list=[user.email],
            fail_silently=False,
        )

        messages.info(request, f"OTP sent to {user.email}")
        return redirect('verify_otp')

    return render(request, "exam/otp_login.html")


# ---------------------------
# Student Dashboard
# ---------------------------
def student_dashboard_view(request):
    if not request.user.is_authenticated or request.user.profile.role != 'student':
        return redirect('login')
    return render(request, 'exam/student_dashboard.html')


# ---------------------------
# Invigilator Dashboard
# ---------------------------
def invigilator_dashboard_view(request):
    if not request.user.is_authenticated or request.user.profile.role != 'invigilator':
        return redirect('login')
    return render(request, 'exam/invigilator_dashboard.html')


# ---------------------------
# Logout
# ---------------------------
def logout_view(request):
    logout(request)
    return redirect('login')
