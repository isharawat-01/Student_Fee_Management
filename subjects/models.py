from django.db import models


class Subject(models.Model):
    subject_name = models.CharField(max_length=100)
    subject_code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    credits = models.PositiveIntegerField(default=4)

    def __str__(self):
        return self.subject_name