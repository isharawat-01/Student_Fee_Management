
from django import forms
from django.db.models import Sum
from .models import FeePayment


class FeePaymentForm(forms.ModelForm):

    class Meta:
        model = FeePayment
        fields = [
            'student',
            'amount',
            'payment_date',
            'payment_mode',
            'transaction_id'
        ]

        widgets = {
            'payment_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'student': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'amount': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter payment amount',
                    'min': '0.01',
                    'step': '0.01'
                }
            ),
            'payment_mode': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'transaction_id': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter transaction ID (optional)'
                }
            ),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        student = self.cleaned_data.get('student')

        if amount is None or student is None:
            return amount

        already_paid = student.payments.aggregate(
            total=Sum('amount')
        )['total'] or 0

        remaining = student.course.total_fees - already_paid

        if amount > remaining:
            raise forms.ValidationError(
                f"Payment exceeds remaining fees of Rs. {remaining}."
            )

        return amount
