from django.contrib import admin
from .models import (
    Profile,
    Branch,
    Semester,
    Student,
    Invigilator,
    Exam,
    ExamTiming
)

admin.site.register(Profile)
admin.site.register(Branch)
admin.site.register(Semester)
admin.site.register(Student)
admin.site.register(Invigilator)
admin.site.register(Exam)
admin.site.register(ExamTiming)
