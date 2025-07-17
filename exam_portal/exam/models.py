from django.db import models
from django.contrib.auth.models import User

# Exam model
class Exam(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()

    def __str__(self):
        return self.title

# User Profile model (to track role)
class Profile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('invigilator', 'Invigilator'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    secret_key = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

# ✅ NewExamResult model (FIXED)
class NewExamResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)  # ✅ Ensure this field exists
    score = models.IntegerField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.exam.title} - Score: {self.score}"
