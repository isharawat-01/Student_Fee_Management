
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_date
from django.utils import timezone
from django.db import models
from django.db.models import Sum

from students.models import Student
from .models import Book, BookIssue
from .services import issue_book, return_book


# Fine Payment
@login_required
def pay_fine(request, issue_id):

    issue = get_object_or_404(BookIssue, id=issue_id)

    if issue.status != "Returned":
        messages.error(
            request,
            "Fine payment is allowed only after returning the book."
        )
        return redirect("issued_books")

    pending_fine = max(
        issue.fine - issue.paid_fine,
        Decimal("0.00")
    )

    if request.method == "POST":

        try:
            amount = request.POST.get("paid_fine")
            payment_date = parse_date(
                request.POST.get("payment_date", "")
            )

            if not amount or not payment_date:
                raise ValidationError(
                    "Please enter payment amount and date."
                )

            amount = Decimal(amount)

            if not amount.is_finite():
                raise ValidationError(
                    "Please enter a valid payment amount."
                )

            if amount <= 0:
                raise ValidationError(
                    "Payment amount must be greater than zero."
                )

            if payment_date > timezone.localdate():
                raise ValidationError(
                    "Payment date cannot be in the future."
                )

            if amount > pending_fine:
                raise ValidationError(
                    "Payment cannot exceed the pending fine."
                )

            issue.paid_fine += amount
            issue.payment_date = payment_date

            issue.save(
                update_fields=["paid_fine", "payment_date"]
            )

            messages.success(
                request,
                "Fine payment recorded successfully!"
            )

            return redirect("issued_books")

        except (ValidationError, ValueError, ArithmeticError) as error:
            messages.error(request, str(error))

    return render(request, "library/pay_fine.html", {
        "issue": issue,
        "pending_fine": pending_fine
    })


# Book List with Search
@login_required
def book_list(request):

    books = Book.objects.select_related("category").all()

    search_query = request.GET.get("search", "").strip()

    if search_query:
        books = books.filter(
            models.Q(title__icontains=search_query) |
            models.Q(author__icontains=search_query) |
            models.Q(isbn__icontains=search_query)
        )

    return render(request, "library/book_list.html", {
        "books": books,
        "search_query": search_query
    })


# Issue Book
@login_required
def issue_book_view(request):

    if request.method == "POST":

        student_id = request.POST.get("student")
        book_id = request.POST.get("book")
        issue_date = parse_date(request.POST.get("issue_date", ""))
        due_date = parse_date(request.POST.get("due_date", ""))

        try:
            student = get_object_or_404(Student, id=student_id)

            if not issue_date or not due_date:
                raise ValidationError(
                    "Please enter valid issue and due dates."
                )

            issue_book(student, book_id, issue_date, due_date)

            messages.success(request, "Book issued successfully!")
            return redirect("book_list")

        except (ValidationError, Book.DoesNotExist) as error:
            messages.error(request, str(error))

    students = Student.objects.all()
    books = Book.objects.filter(available_copies__gt=0)

    return render(request, "library/issue_book.html", {
        "students": students,
        "books": books
    })


# Return Book
@login_required
def return_book_view(request, issue_id):

    issue = get_object_or_404(BookIssue, id=issue_id)

    if request.method == "POST":

        try:
            return_book(issue_id)
            messages.success(request, "Book returned successfully!")

        except ValidationError as error:
            messages.error(request, str(error))

        return redirect("issued_books")

    return render(request, "library/return_book.html", {
        "issue": issue
    })


# Issued Books with Overdue and Pending Fine
@login_required
def issued_books(request):

    issues = BookIssue.objects.select_related(
        "student", "book"
    ).all().order_by("-issue_date")

    today = timezone.localdate()

    for issue in issues:

        issue.is_overdue = (
            issue.status == "Issued"
            and issue.due_date < today
        )

        if issue.status == "Returned":

            issue.pending_fine = max(
                issue.fine - issue.paid_fine,
                Decimal("0.00")
            )

        elif issue.is_overdue:

            late_days = (today - issue.due_date).days
            issue.pending_fine = Decimal(late_days) * Decimal("5.00")

        else:
            issue.pending_fine = Decimal("0.00")

    return render(request, "library/issued_books.html", {
        "issues": issues
    })


# Library Dashboard
@login_required
def library_dashboard(request):

    total_books = Book.objects.aggregate(
        total=Sum("total_copies")
    )["total"] or 0

    available_books = Book.objects.aggregate(
        total=Sum("available_copies")
    )["total"] or 0

    issued_books_count = BookIssue.objects.filter(
        status="Issued"
    ).count()

    overdue_books = BookIssue.objects.filter(
        status="Issued",
        due_date__lt=timezone.localdate()
    ).count()

    context = {
        "total_books": total_books,
        "available_books": available_books,
        "issued_books_count": issued_books_count,
        "overdue_books": overdue_books,
    }

    return render(request, "library/dashboard.html", context)
