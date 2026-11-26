
from django.contrib import admin
from .models import BookCategory, Book, BookIssue


@admin.register(BookCategory)
class BookCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'isbn',
        'category',
        'total_copies',
        'available_copies'
    )

    list_filter = ('category',)
    search_fields = ('title', 'author', 'isbn')


@admin.register(BookIssue)
class BookIssueAdmin(admin.ModelAdmin):

    list_display = (
        'student',
        'book',
        'issue_date',
        'due_date',
        'return_date',
        'fine',
        'paid_fine',
        'payment_date',
        'payment_status',
        'status'
    )

    list_filter = (
        'status',
        'payment_date',
        'issue_date'
    )

    search_fields = (
        'student__student_id',
        'book__title'
    )
