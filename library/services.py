from datetime import date
from decimal import Decimal


from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Book, BookIssue


@transaction.atomic
def issue_book(student, book_id, issue_date, due_date):

    book = Book.objects.select_for_update().get(id=book_id)

    if book.available_copies <= 0:
        raise ValidationError("This book is currently unavailable.")

    if due_date < issue_date:
        raise ValidationError("Due date cannot be before issue date.")

    book.available_copies -= 1
    book.save(update_fields=["available_copies"])

    book_issue = BookIssue.objects.create(
        student=student,
        book=book,
        issue_date=issue_date,
        due_date=due_date
    )

    return book_issue



@transaction.atomic
def return_book(issue_id, return_date=None):

    issue = BookIssue.objects.select_for_update().get(id=issue_id)

    if issue.status == "Returned":
        raise ValidationError("This book has already been returned.")

    if return_date is None:
        return_date = date.today()

    if return_date < issue.issue_date:
        raise ValidationError("Return date cannot be before issue date.")

    # Calculate late fine: Rs. 5 per day
    late_days = max((return_date - issue.due_date).days, 0)
    fine = Decimal(late_days) * Decimal("5.00")

    issue.return_date = return_date
    issue.fine = fine
    issue.status = "Returned"
    issue.save()

    book = Book.objects.select_for_update().get(id=issue.book_id)
    book.available_copies += 1
    book.save(update_fields=["available_copies"])

    return issue