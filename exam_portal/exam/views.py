from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from .models import Profile, Exam, NewExamResult
import pyotp
import random
import time
import qrcode
import base64
from io import BytesIO

OTP_EXPIRY_SECONDS = 300  # 5 minutes
OTP_MAX_ATTEMPTS = 3

# ---------------------------
# Home redirect to login
# ---------------------------
def home_redirect(request):
    return redirect('login')


# ---------------------------
# Register View
# ---------------------------
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = False
            user.save()

            # Save role into profile (created via signal)
            user.profile.role = form.cleaned_data['role']
            user.profile.save()

            # Generate OTP
            otp = str(random.randint(100000, 999999))
            request.session['otp'] = otp
            request.session['username'] = user.username
            request.session['otp_time'] = int(time.time())
            request.session['otp_attempts'] = OTP_MAX_ATTEMPTS

            # Send OTP via email
            send_mail(
                subject="Exam Portal Email Verification OTP",
                message=f"Your OTP is: {otp}",
                from_email="noreply@exam.com",
                recipient_list=[user.email],
                fail_silently=False,
            )

            messages.info(request, f"OTP sent to {user.email}")
            return redirect('verify_otp')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


# ---------------------------
# OTP Verification View
# ---------------------------
def verify_otp_view(request):
    if request.method == 'POST':
        input_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')
        username = request.session.get('username')
        otp_time = request.session.get('otp_time')
        attempts = request.session.get('otp_attempts', OTP_MAX_ATTEMPTS)

        if not all([input_otp, session_otp, username, otp_time]):
            messages.error(request, "Session expired or incomplete.")
            return redirect('register')

        if int(time.time()) - int(otp_time) > OTP_EXPIRY_SECONDS:
            messages.error(request, "OTP expired.")
            return redirect('register')

        if input_otp != session_otp:
            attempts -= 1
            request.session['otp_attempts'] = attempts
            if attempts <= 0:
                messages.error(request, "Too many failed attempts. Start again.")
                return redirect('register')
            messages.error(request, f"Invalid OTP. {attempts} attempts left.")
            return redirect('verify_otp')

        # OTP matched
        user = User.objects.get(username=username)
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('google_otp_setup')

    return render(request, 'exam/verify_otp.html')


# ---------------------------
# Google Authenticator Setup View
# ---------------------------
@login_required
def google_otp_setup(request):
    user = request.user
    if not user.profile.otp_secret:
        otp_secret = pyotp.random_base32()
        user.profile.otp_secret = otp_secret
        user.profile.save()
    else:
        otp_secret = user.profile.otp_secret

    totp = pyotp.TOTP(otp_secret)
    otp_uri = totp.provisioning_uri(name=user.username, issuer_name="Exam Portal")

    qr = qrcode.make(otp_uri)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'exam/google_otp_setup.html', {
        'qr_code_base64': img_str,
        'show_continue': True
    })


# ---------------------------
# Login View
# ---------------------------
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user and user.is_active:
            request.session['temp_user'] = user.username
            return redirect('google_otp_verify')
        else:
            messages.error(request, "Invalid credentials or inactive account.")
    return render(request, 'exam/login.html')


# ---------------------------
# Google OTP Verify
# ---------------------------
def google_otp_verify(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        username = request.session.get('temp_user')

        if not username:
            messages.error(request, "Session expired. Please login again.")
            return redirect('login')

        try:
            user = User.objects.get(username=username)
            totp = pyotp.TOTP(user.profile.otp_secret)
            if totp.verify(code):
                login(request, user)
                role = user.profile.role
                if role == 'student':
                    return redirect('student_dashboard')
                else:
                    return redirect('invigilator_dashboard')
            else:
                messages.error(request, "Invalid Google Authenticator code.")
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('login')

    return render(request, 'exam/google_otp_verify.html')


@login_required
def take_exam_view(request, exam_id):
    exam = Exam.objects.get(id=exam_id)

    if request.method == 'POST':
        # Placeholder: You can collect answers and calculate scores here
        score = int(request.POST.get('score', 0))  # Assume simple manual input for demo
        NewExamResult.objects.create(user=request.user, exam=exam, score=score)
        messages.success(request, "Exam submitted successfully.")
        return redirect('student_dashboard')

    return render(request, 'exam/take_exam.html', {'exam': exam})


# ---------------------------
# OTP Login View (email only)
# ---------------------------
def otp_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "User does not exist.")
            return redirect("otp_login")

        otp = str(random.randint(100000, 999999))
        request.session['otp'] = otp
        request.session['username'] = username
        request.session['otp_type'] = 'login'
        request.session['otp_time'] = int(time.time())
        request.session['otp_attempts'] = OTP_MAX_ATTEMPTS

        send_mail(
            subject="Exam Portal Login OTP",
            message=f"Your OTP is: {otp}",
            from_email="noreply@exam.com",
            recipient_list=[user.email],
            fail_silently=False,
        )

        messages.info(request, f"OTP sent to {user.email}")
        return redirect('verify_otp')

    return render(request, "exam/otp_login.html")


# ---------------------------
# Student Dashboard
# ---------------------------
@login_required
def student_dashboard_view(request):
    if request.user.profile.role != 'student':
        return redirect('login')
    return render(request, 'exam/student_dashboard.html')


# ---------------------------
# Invigilator Dashboard
# ---------------------------
@login_required
def invigilator_dashboard_view(request):
    if request.user.profile.role != 'invigilator':
        return redirect('login')
    return render(request, 'exam/invigilator_dashboard.html')

@login_required
def view_results(request):
    results = NewExamResult.objects.filter(user=request.user)
    return render(request, 'exam/view_results.html', {'results': results})

# ---------------------------
# Logout
# ---------------------------
def logout_view(request):
    logout(request)
    return redirect('login')



# #✅ Multiple-choice question (MCQ) exam logic with auto score calculation?
# ✅ Separate exam list page for students to choose and start?
# ✅ Role-based dashboard view of available exams/results?

# Let me know what you'd like to expand next!