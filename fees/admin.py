
from django.contrib import admin
from .models import FeePayment


@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'amount',
        'payment_date',
        'payment_mode',
        'transaction_id'
    )

    search_fields = (
        'student__student_id',
        'student__user__username',
        'transaction_id'
    )

    list_filter = ('payment_mode', 'payment_date')
