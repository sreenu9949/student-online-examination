from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# ---------------------------
# Profile: User Role Mapping
# ---------------------------
class Profile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('invigilator', 'Invigilator'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# Automatically create or update profile when a User is created
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()


# ---------------------------
# Branch Model
# ---------------------------
class Branch(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# ---------------------------
# Semester Model
# ---------------------------
class Semester(models.Model):
    name = models.CharField(max_length=50)  # e.g., "1st Sem", "2nd Sem"

    def __str__(self):
        return self.name


# ---------------------------
# Student Model
# ---------------------------
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True)
    semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Student: {self.user.username}"


# ---------------------------
# Invigilator Model
# ---------------------------
class Invigilator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)

    def __str__(self):
        return f"Invigilator: {self.user.username}"


# ---------------------------
# Exam Model
# ---------------------------
class Exam(models.Model):
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} - {self.subject}"


# ---------------------------
# Exam Timing Slot Model
# ---------------------------
class ExamTiming(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.exam.title} | {self.start_time} - {self.end_time}"


# ---------------------------
# Exam Result / Marks Model
# ---------------------------
class ExamResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    marks_obtained = models.FloatField()
    max_marks = models.FloatField(default=100)
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('student', 'exam')

    @property
    def percentage(self):
        return (self.marks_obtained / self.max_marks) * 100 if self.max_marks else 0

    @property
    def is_passed(self):
        return self.percentage >= 35

    def __str__(self):
        return f"{self.student.user.username} - {self.exam.title} : {self.marks_obtained}/{self.max_marks}"
