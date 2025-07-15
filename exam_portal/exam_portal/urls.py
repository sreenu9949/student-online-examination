from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', include('exam.urls')),  # Your app's login URL
    path('', lambda request: redirect('login/')),  # <== Redirect root to /login/
]
