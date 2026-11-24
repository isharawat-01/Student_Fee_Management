from django.contrib import admin
from .models import Timetable


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):

    list_display = (
        'course_subject',
        'employee',
        'day',
        'start_time',
        'end_time',
        'room_number',
    )

    list_filter = (
        'day',
        'employee',
    )

    search_fields = (
        'course_subject__course__course_name',
        'course_subject__subject__subject_name',
        'employee__full_name',
        'room_number',
    )

    ordering = ('day', 'start_time')