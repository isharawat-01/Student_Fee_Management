
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db import transaction
from uuid import uuid4

from .models import Student, Course


def register(request):

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        course_id = request.POST.get('course')

        if not all([full_name, username, email, phone, password, course_id]):
            messages.error(request, 'All fields are required.')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('register')

        try:
            course = Course.objects.get(id=course_id)

            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=full_name
                )

                Student.objects.create(
                    user=user,
                    student_id='STU' + uuid4().hex[:8].upper(),
                    phone=phone,
                    course=course
                )

            messages.success(request, 'Registration successful! Please login.')
            return redirect('student_login')

        except Course.DoesNotExist:
            messages.error(request, 'Please select a valid course.')

    courses = Course.objects.all()
    return render(request, 'students/register.html', {'courses': courses})


def student_login(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            if user.is_superuser:
                messages.error(request, 'Please use the admin login.')
                return redirect('student_login')

            if Student.objects.filter(user=user).exists():
                login(request, user)
                return redirect('student_dashboard')

        messages.error(request, 'Invalid username or password.')

    return render(request, 'students/login.html')


@login_required
def student_dashboard(request):

    try:
        student = Student.objects.select_related(
            'user', 'course'
        ).get(user=request.user)

    except Student.DoesNotExist:
        logout(request)
        messages.error(request, 'Student profile not found.')
        return redirect('student_login')

    paid_fees = student.payments.aggregate(
        total=Sum('amount')
    )['total'] or 0

    total_fees = student.course.total_fees
    remaining_fees = total_fees - paid_fees

    return render(request, 'students/dashboard.html', {
        'student': student,
        'total_fees': total_fees,
        'paid_fees': paid_fees,
        'remaining_fees': remaining_fees,
        'payments': student.payments.order_by('-payment_date')
    })


@login_required
def student_logout(request):

    if request.method == 'POST':
        logout(request)

    return redirect('student_login')
