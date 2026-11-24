from django.db import models


class Employee(models.Model):

    DESIGNATION_CHOICES = [
        ('Professor', 'Professor'),
        ('Associate Professor', 'Associate Professor'),
        ('Assistant Professor', 'Assistant Professor'),
        ('HOD', 'HOD'),
        ('Administrative Staff', 'Administrative Staff'),
        ('Other', 'Other'),
    ]

    employee_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    designation = models.CharField(
        max_length=50,
        choices=DESIGNATION_CHOICES
    )
    department = models.CharField(max_length=100)
    date_of_joining = models.DateField()

    def __str__(self):
        return f"{self.employee_id} - {self.full_name}"