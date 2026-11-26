
from django.db import models
from students.models import Student


class BookCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=150)
    isbn = models.CharField(max_length=20, unique=True)

    category = models.ForeignKey(
        BookCategory,
        on_delete=models.PROTECT,
        related_name="books"
    )

    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)

    published_year = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title


class BookIssue(models.Model):

    STATUS_CHOICES = [
        ("Issued", "Issued"),
        ("Returned", "Returned"),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="book_issues"
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.PROTECT,
        related_name="issues"
    )

    issue_date = models.DateField()
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)

    fine = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    # Fine Payment Details
    paid_fine = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    payment_date = models.DateField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="Issued"
    )

    @property
    def payment_status(self):

        if self.fine <= 0:
            return "No Fine"

        if self.paid_fine >= self.fine:
            return "Paid"

        if self.paid_fine > 0:
            return "Partial"

        return "Unpaid"

    def __str__(self):
        return f"{self.student} - {self.book}"
