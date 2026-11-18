
from django.db import models
from django.core.validators import MinValueValidator
from students.models import Student


class FeePayment(models.Model):

    PAYMENT_MODES = [
        ('Cash', 'Cash'),
        ('UPI', 'UPI'),
        ('Card', 'Card'),
        ('Bank Transfer', 'Bank Transfer'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name='payments'
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    payment_date = models.DateField()

    payment_mode = models.CharField(
        max_length=20,
        choices=PAYMENT_MODES
    )

    transaction_id = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.student_id} - Rs. {self.amount}"
