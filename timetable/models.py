from django.db import models
from courses.models import CourseSubject
from employees.models import Employee


class Timetable(models.Model):

    DAY_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
    ]

    course_subject = models.ForeignKey(
        CourseSubject,
        on_delete=models.CASCADE,
        related_name='timetable_entries'
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name='timetable_entries'
    )

    day = models.CharField(
        max_length=15,
        choices=DAY_CHOICES
    )

    start_time = models.TimeField()
    end_time = models.TimeField()

    room_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.course_subject} - {self.day}"