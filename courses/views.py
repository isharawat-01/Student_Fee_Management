from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Course


def is_admin(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(is_admin, login_url='/admin/login/')
def course_list(request):
    courses = Course.objects.all().order_by('course_name')

    return render(request, 'courses/course_list.html', {
        'courses': courses
    })


@user_passes_test(is_admin, login_url='/admin/login/')
def add_course(request):
    if request.method == 'POST':
        course_name = request.POST.get('course_name', '').strip()
        course_code = request.POST.get('course_code', '').strip()
        duration = request.POST.get('duration', '').strip()
        description = request.POST.get('description', '').strip()

        if not all([course_name, course_code, duration]):
            messages.error(request, 'Please fill all required fields.')

        elif Course.objects.filter(course_code=course_code).exists():
            messages.error(request, 'Course code already exists.')

        else:
            Course.objects.create(
                course_name=course_name,
                course_code=course_code,
                duration=duration,
                description=description
            )
            messages.success(request, 'Course added successfully!')
            return redirect('course_list')

    return render(request, 'courses/course_form.html', {
        'page_title': 'Add Course'
    })


@user_passes_test(is_admin, login_url='/admin/login/')
def edit_course(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if request.method == 'POST':
        course_name = request.POST.get('course_name', '').strip()
        course_code = request.POST.get('course_code', '').strip()
        duration = request.POST.get('duration', '').strip()
        description = request.POST.get('description', '').strip()

        if not all([course_name, course_code, duration]):
            messages.error(request, 'Please fill all required fields.')

        elif Course.objects.filter(
            course_code=course_code
        ).exclude(pk=pk).exists():
            messages.error(request, 'Course code already exists.')

        else:
            course.course_name = course_name
            course.course_code = course_code
            course.duration = duration
            course.description = description
            course.save()

            messages.success(request, 'Course updated successfully!')
            return redirect('course_list')

    return render(request, 'courses/course_form.html', {
        'course': course,
        'page_title': 'Edit Course'
    })


@user_passes_test(is_admin, login_url='/admin/login/')
def delete_course(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if request.method == 'POST':
        try:
            course.delete()
            messages.success(request, 'Course deleted successfully!')
        except Exception:
            messages.error(
                request,
                'This course cannot be deleted because it is in use.'
            )

    return redirect('course_list')