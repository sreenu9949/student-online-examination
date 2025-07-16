from django.contrib import admin
from .models import Profile, Branch, Semester, Student, Invigilator, Exam, ExamTiming, ExamResult

# Import-Export
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields

# -----------------------------
# Profile
# -----------------------------
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role']


# -----------------------------
# Branch & Semester
# -----------------------------
admin.site.register(Branch)
admin.site.register(Semester)


# -----------------------------
# Student
# -----------------------------
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'branch', 'semester']


# -----------------------------
# Invigilator
# -----------------------------
@admin.register(Invigilator)
class InvigilatorAdmin(admin.ModelAdmin):
    list_display = ['user', 'department']

    # Read-only for invigilators
    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# -----------------------------
# Exam
# -----------------------------
@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'branch', 'semester', 'date', 'time']


# -----------------------------
# Exam Timing
# -----------------------------
@admin.register(ExamTiming)
class ExamTimingAdmin(admin.ModelAdmin):
    list_display = ['exam', 'start_time', 'end_time']


# -----------------------------
# ExamResult ImportExport
# -----------------------------
class ExamResultResource(resources.ModelResource):
    student_username = fields.Field(attribute='student__user__username', column_name='Student')
    exam_title = fields.Field(attribute='exam__title', column_name='Exam')

    class Meta:
        model = ExamResult
        fields = ('id', 'student_username', 'exam_title', 'marks_obtained', 'max_marks', 'percentage')
        export_order = ('id', 'student_username', 'exam_title', 'marks_obtained', 'max_marks', 'percentage')


@admin.register(ExamResult)
class ExamResultAdmin(ImportExportModelAdmin):
    resource_class = ExamResultResource
    list_display = ('student', 'exam', 'marks_obtained', 'max_marks', 'percentage', 'is_passed')
    list_filter = ('exam',)
    search_fields = ('student__user__username', 'exam__title')

    def percentage(self, obj):
        return f"{obj.percentage:.2f}%"

    def is_passed(self, obj):
        return "✅ Pass" if obj.is_passed else "❌ Fail"
    is_passed.short_description = 'Status'
