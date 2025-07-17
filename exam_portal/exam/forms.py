from django import forms
from django.contrib.auth.models import User

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    role = forms.ChoiceField(choices=[('student', 'Student'), ('invigilator', 'Invigilator')])

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
