from django.contrib import admin
from .models import Course, CourseSubject


class CourseSubjectInline(admin.TabularInline):
    model = CourseSubject
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_name', 'course_code', 'duration')
    search_fields = ('course_name', 'course_code')
    inlines = [CourseSubjectInline]


@admin.register(CourseSubject)
class CourseSubjectAdmin(admin.ModelAdmin):
    list_display = ('course', 'subject', 'semester')
    list_filter = ('course', 'semester')