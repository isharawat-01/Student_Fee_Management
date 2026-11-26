
from datetime import date, timedelta

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone

from students.models import Student, Course
from fees.models import FeePayment
from attendance.models import Attendance
from employees.models import Employee


@login_required
def home(request):

    today = timezone.localdate()

    # Overall Statistics
    total_students = Student.objects.count()
    total_employees = Employee.objects.count()
    total_courses = Course.objects.count()

    # Fee Collection and Pending Fees
    pending_fees = 0

    for student in Student.objects.select_related('course'):

        paid = student.payments.aggregate(
            total=Sum('amount')
        )['total'] or 0

        pending_fees += max(
            student.course.total_fees - paid, 0
        )

    # Date Range Filter
    selected_range = request.GET.get('range', '6m')

    start_date = today
    end_date = today

    if selected_range == '7d':
        start_date = today - timedelta(days=6)

    elif selected_range == '30d':
        start_date = today - timedelta(days=29)

    elif selected_range == 'custom':

        try:
            start_date = date.fromisoformat(
                request.GET.get('start_date', '')
            )

            end_date = date.fromisoformat(
                request.GET.get('end_date', '')
            )

            if start_date > end_date or start_date > today:
                raise ValueError

            if end_date > today:
                end_date = today

        except (ValueError, TypeError):
            selected_range = '6m'

    else:
        selected_range = '6m'

    if selected_range == '6m':

        start_date = today.replace(day=1)

        for _ in range(5):

            if start_date.month == 1:
                start_date = start_date.replace(
                    year=start_date.year - 1,
                    month=12
                )
            else:
                start_date = start_date.replace(
                    month=start_date.month - 1
                )

        end_date = today

    # Payments and Attendance Querysets
    payment_queryset = FeePayment.objects.filter(
        payment_date__range=(start_date, end_date)
    )

    attendance_queryset = Attendance.objects.filter(
        date__range=(start_date, end_date)
    )

    total_collection = payment_queryset.aggregate(
        total=Sum('amount')
    )['total'] or 0

    # Attendance Statistics
    attendance_data = attendance_queryset.aggregate(
        present=Count(
            'id',
            filter=Q(status='Present')
        ),
        absent=Count(
            'id',
            filter=Q(status='Absent')
        ),
        late=Count(
            'id',
            filter=Q(status='Late')
        )
    )

    # Recent Payments
    recent_payments = (
        payment_queryset
        .select_related('student__user')
        .order_by('-payment_date', '-created_at')[:5]
    )

    # Recent Attendance
    recent_attendance = (
        attendance_queryset
        .select_related('student__user')
        .order_by('-date', '-id')[:5]
    )

    # Fee Collection Chart
    chart_payments = payment_queryset.order_by(
        'payment_date'
    ).values('payment_date', 'amount')

    collection_totals = {}

    if (end_date - start_date).days <= 31:
        date_format = '%d %b'
    else:
        date_format = '%b %Y'

    for payment in chart_payments:

        label = payment['payment_date'].strftime(date_format)

        collection_totals[label] = (
            collection_totals.get(label, 0)
            + float(payment['amount'])
        )

    collection_labels = list(collection_totals.keys())

    collection_values = list(collection_totals.values())

    # Dashboard Context
    context = {
        'total_students': total_students,
        'total_employees': total_employees,
        'total_courses': total_courses,

        'total_collection': total_collection,
        'pending_fees': pending_fees,

        'collection_labels': collection_labels,
        'collection_values': collection_values,

        'attendance_data': attendance_data,

        'recent_payments': recent_payments,
        'recent_attendance': recent_attendance,

        'selected_range': selected_range,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(
        request,
        'dashboard/home.html',
        context
    )
