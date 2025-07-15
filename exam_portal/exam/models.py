from django.db import models
from django.contrib.auth.models import User

# User Role Profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)

# Branch
class Branch(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Semester (Optional but often used in academic systems)
class Semester(models.Model):
    name = models.CharField(max_length=50)  # e.g., "1st Sem", "2nd Sem"

    def __str__(self):
        return self.name

# Student Model
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True)
    semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.username

# Invigilator Model
class Invigilator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username

# Exam Model
class Exam(models.Model):
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} - {self.subject}"

# Exam Timing (extra for schedule slots)
class ExamTiming(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.exam.title} | {self.start_time} - {self.end_time}"
