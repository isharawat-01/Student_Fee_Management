
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum
from django.http import FileResponse, Http404

from students.models import Student
from .models import FeePayment
from .forms import FeePaymentForm
from .receipt import generate_fee_receipt


def is_admin(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(is_admin, login_url='/admin/login/')
def admin_dashboard(request):

    total_students = Student.objects.count()

    total_payments = FeePayment.objects.count()

    total_collected = FeePayment.objects.aggregate(
        total=Sum('amount')
    )['total'] or 0

    students = Student.objects.select_related(
        'user', 'course'
    ).order_by('-admission_date')[:10]

    recent_payments = FeePayment.objects.select_related(
        'student', 'student__user'
    ).order_by('-created_at')[:10]

    return render(request, 'fees/admin_dashboard.html', {
        'total_students': total_students,
        'total_payments': total_payments,
        'total_collected': total_collected,
        'students': students,
        'recent_payments': recent_payments,
    })


@user_passes_test(is_admin, login_url='/admin/login/')
def add_fee(request):

    if request.method == 'POST':
        form = FeePaymentForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Fee payment added successfully!'
            )
            return redirect('admin_dashboard')

    else:
        form = FeePaymentForm()

    return render(request, 'fees/add_fee.html', {
        'form': form
    })


@user_passes_test(is_admin, login_url='/admin/login/')
def download_receipt(request, payment_id):

    try:
        payment = FeePayment.objects.select_related(
            'student',
            'student__user',
            'student__course'
        ).get(id=payment_id)

    except FeePayment.DoesNotExist:
        raise Http404("Fee receipt not found.")

    pdf_buffer = generate_fee_receipt(payment)

    return FileResponse(
        pdf_buffer,
        as_attachment=True,
        filename=f"Fee_Receipt_{payment.id}.pdf",
        content_type='application/pdf'
    )

from django.contrib.auth.decorators import login_required


@login_required
def student_download_receipt(request, payment_id):

    try:
        student = Student.objects.get(user=request.user)

        payment = FeePayment.objects.select_related(
            'student',
            'student__user',
            'student__course'
        ).get(
            id=payment_id,
            student=student
        )

    except (Student.DoesNotExist, FeePayment.DoesNotExist):
        raise Http404("Fee receipt not found.")

    pdf_buffer = generate_fee_receipt(payment)

    return FileResponse(
        pdf_buffer,
        as_attachment=True,
        filename=f"Fee_Receipt_{payment.id}.pdf",
        content_type='application/pdf'
    )
