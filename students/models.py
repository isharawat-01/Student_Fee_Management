
from django.db import models
from django.contrib.auth.models import User


class Course(models.Model):
    course_name = models.CharField(max_length=100)
    duration = models.CharField(max_length=50)
    total_fees = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.course_name


class Student(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    student_id = models.CharField(max_length=20, unique=True)
    phone = models.CharField(max_length=15)
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name='students'
    )
    admission_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_id} - {self.user.get_full_name() or self.user.username}"
