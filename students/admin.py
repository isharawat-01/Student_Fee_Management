
from django.contrib import admin
from .models import Course, Student


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'course_name', 'duration', 'total_fees')
    search_fields = ('course_name',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'student_id',
        'user',
        'phone',
        'course',
        'admission_date'
    )
    search_fields = ('student_id', 'user__username', 'user__email')
    list_filter = ('course',)
