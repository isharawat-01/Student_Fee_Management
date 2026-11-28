from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from .models import Subject


def is_admin(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(is_admin, login_url='/admin/login/')
def subject_list(request):
    subjects = Subject.objects.all().order_by('subject_name')
    return render(request, 'subjects/subject_list.html', {'subjects': subjects})


@user_passes_test(is_admin, login_url='/admin/login/')
def add_subject(request):
    if request.method == 'POST':
        subject_name = request.POST.get('subject_name', '').strip()
        subject_code = request.POST.get('subject_code', '').strip()
        credits = request.POST.get('credits', '').strip()
        description = request.POST.get('description', '').strip()

        if not all([subject_name, subject_code, credits]):
            messages.error(request, 'Please fill all required fields.')

        elif Subject.objects.filter(subject_code=subject_code).exists():
            messages.error(request, 'Subject code already exists.')

        else:
            try:
                credits = int(credits)
                if credits < 1:
                    raise ValueError

                Subject.objects.create(
                    subject_name=subject_name,
                    subject_code=subject_code,
                    credits=credits,
                    description=description
                )

                messages.success(request, 'Subject added successfully!')
                return redirect('subject_list')

            except ValueError:
                messages.error(request, 'Credits must be a positive number.')

    return render(request, 'subjects/subject_form.html', {'page_title': 'Add Subject'})


@user_passes_test(is_admin, login_url='/admin/login/')
def edit_subject(request, pk):
    subject = get_object_or_404(Subject, pk=pk)

    if request.method == 'POST':
        subject_name = request.POST.get('subject_name', '').strip()
        subject_code = request.POST.get('subject_code', '').strip()
        credits = request.POST.get('credits', '').strip()
        description = request.POST.get('description', '').strip()

        if not all([subject_name, subject_code, credits]):
            messages.error(request, 'Please fill all required fields.')

        elif Subject.objects.filter(subject_code=subject_code).exclude(pk=pk).exists():
            messages.error(request, 'Subject code already exists.')

        else:
            try:
                credits = int(credits)
                if credits < 1:
                    raise ValueError

                subject.subject_name = subject_name
                subject.subject_code = subject_code
                subject.credits = credits
                subject.description = description
                subject.save()

                messages.success(request, 'Subject updated successfully!')
                return redirect('subject_list')

            except ValueError:
                messages.error(request, 'Credits must be a positive number.')

    return render(
        request,
        'subjects/subject_form.html',
        {'subject': subject, 'page_title': 'Edit Subject'}
    )


@user_passes_test(is_admin, login_url='/admin/login/')
def delete_subject(request, pk):
    subject = get_object_or_404(Subject, pk=pk)

    if request.method == 'POST':
        if subject.subject_courses.exists():
            messages.error(
                request,
                'This subject is assigned to a course and cannot be deleted.'
            )
        else:
            subject.delete()
            messages.success(request, 'Subject deleted successfully!')

    return redirect('subject_list')