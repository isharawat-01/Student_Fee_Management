from django.db import models
from subjects.models import Subject


class Course(models.Model):
    course_name = models.CharField(max_length=100)
    course_code = models.CharField(max_length=20, unique=True)
    duration = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.course_name


class CourseSubject(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='course_subjects'
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='subject_courses'
    )

    semester = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('course', 'subject', 'semester')

    def __str__(self):
        return f"{self.course} - {self.subject}"