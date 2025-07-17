from django.contrib import admin
from .models import Exam, NewExamResult


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['title', 'date']

@admin.register(NewExamResult)
class NewExamResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'exam', 'score']  # ✅ use 'exam', not 'exa'
