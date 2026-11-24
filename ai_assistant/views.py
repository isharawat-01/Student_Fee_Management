
import logging

from django.shortcuts import render
from django.db import transaction, IntegrityError

from attendance.models import Attendance
from students.models import Student
from courses.models import CourseSubject
from employees.models import Employee
from django.contrib.auth.decorators import login_required

from .services import (
    generate_sql,
    execute_read_only_sql,
    extract_timetable_data,
    extract_attendance_data,
)

from .forms import (
    TimetableImageForm,
    TimetableEntryFormSet,
    AttendanceImageForm,
    AttendanceEntryFormSet,
)


logger = logging.getLogger(__name__)


# ==========================================
# AI CHAT - NATURAL LANGUAGE TO SQL
# ==========================================

@login_required
def ai_chat(request):

    answer = None
    generated_sql = None
    error = None

    if request.method == "POST":

        question = request.POST.get("question", "").strip()

        if question:

            try:
                generated_sql = generate_sql(question)
                answer = execute_read_only_sql(generated_sql)

            except Exception:
                logger.exception("AI chat error")
                error = (
                    "Sorry, something went wrong while processing "
                    "your question. Please try again."
                )

        else:
            error = "Please enter a question."

    return render(
        request,
        "ai_assistant/chat.html",
        {
            "answer": answer,
            "generated_sql": generated_sql,
            "error": error,
        }
    )


# ==========================================
# TIMETABLE IMAGE UPLOAD AND EXTRACTION
# ==========================================

@login_required
def upload_timetable(request):

    form = TimetableImageForm()
    entry_formset = None
    extracted_data = None
    error = None

    if request.method == "POST":

        form = TimetableImageForm(request.POST, request.FILES)

        if form.is_valid():

            try:

                image = form.cleaned_data["timetable_image"]

                extracted_data = extract_timetable_data(image)

                initial_data = []

                for entry in extracted_data.get("entries", []):

                    course_subject = None
                    employee = None

                    course_name = entry.get("course")
                    subject_name = entry.get("subject")
                    employee_name = entry.get("employee")
                    semester = entry.get("semester")

                    if course_name and subject_name:

                        course_subject = CourseSubject.objects.filter(
                            course__course_name__iexact=course_name,
                            subject__subject_name__iexact=subject_name,
                            semester=semester
                        ).first()

                    if employee_name:

                        employee = Employee.objects.filter(
                            full_name__iexact=employee_name
                        ).first()

                    initial_data.append({
                        "course_subject": course_subject,
                        "employee": employee,
                        "day": entry.get("day") or "",
                        "start_time": entry.get("start_time") or "",
                        "end_time": entry.get("end_time") or "",
                        "room_number": entry.get("room_number") or "",
                    })

                entry_formset = TimetableEntryFormSet(
                    initial=initial_data
                )

                if not initial_data:
                    error = "No timetable entries could be extracted. Please upload a clearer image."

            except Exception:
                logger.exception("Timetable extraction error")
                error = (
                    "Unable to extract the timetable. "
                    "Please check the image and try again."
                )

        else:
            error = "Please upload a valid timetable image."

    return render(
        request,
        "ai_assistant/upload_timetable.html",
        {
            "form": form,
            "extracted_data": extracted_data,
            "entry_formset": entry_formset,
            "error": error,
        }
    )


# ==========================================
# SAVE TIMETABLE WITH TIME VALIDATION
# ==========================================

@login_required
def save_timetable(request):

    if request.method == "POST":

        formset = TimetableEntryFormSet(request.POST)

        if formset.is_valid():

            time_error = False

            # Additional server-side validation
            for entry_form in formset:

                start_time = entry_form.cleaned_data.get("start_time")
                end_time = entry_form.cleaned_data.get("end_time")

                if not start_time:
                    entry_form.add_error(
                        "start_time",
                        "Start time is required."
                    )
                    time_error = True

                if not end_time:
                    entry_form.add_error(
                        "end_time",
                        "End time is required."
                    )
                    time_error = True

                if start_time and end_time and end_time <= start_time:
                    entry_form.add_error(
                        "end_time",
                        "End time must be later than start time."
                    )
                    time_error = True

            if time_error:

                return render(
                    request,
                    "ai_assistant/upload_timetable.html",
                    {
                        "form": TimetableImageForm(),
                        "entry_formset": formset,
                        "error": "Please correct the timetable time errors.",
                    }
                )

            saved_count = 0

            try:

                with transaction.atomic():

                    for entry_form in formset:
                        entry_form.save()
                        saved_count += 1

                return render(
                    request,
                    "ai_assistant/upload_timetable.html",
                    {
                        "form": TimetableImageForm(),
                        "success_message": (
                            f"{saved_count} timetable entries saved successfully!"
                        ),
                    }
                )

            except Exception:
                logger.exception("Timetable saving error")

                return render(
                    request,
                    "ai_assistant/upload_timetable.html",
                    {
                        "form": TimetableImageForm(),
                        "entry_formset": formset,
                        "error": (
                            "Unable to save timetable entries. "
                            "Please check the details and try again."
                        ),
                    }
                )

        else:

            logger.warning(
                "Timetable form errors: %s",
                formset.errors
            )

            return render(
                request,
                "ai_assistant/upload_timetable.html",
                {
                    "form": TimetableImageForm(),
                    "entry_formset": formset,
                    "error": "Please correct the errors in the timetable form.",
                }
            )

    return render(
        request,
        "ai_assistant/upload_timetable.html",
        {
            "form": TimetableImageForm()
        }
    )


# ==========================================
# HELPER: FIND STUDENT
# ==========================================

def find_student(student_id=None, student_name=None):

    student = None

    # First try matching Student ID
    if student_id:

        student = Student.objects.filter(
            student_id__iexact=student_id.strip()
        ).first()

    if student:
        return student

    # If ID does not match, try matching full name
    if student_name:

        student_name = " ".join(student_name.strip().split())

        if student_name:

            # Case 1: Full name stored in first_name
            student = Student.objects.filter(
                user__first_name__iexact=student_name
            ).first()

            if student:
                return student

            # Case 2: First name and last name stored separately
            name_parts = student_name.split()

            if len(name_parts) >= 2:

                first_name = name_parts[0]
                last_name = " ".join(name_parts[1:])

                student = Student.objects.filter(
                    user__first_name__iexact=first_name,
                    user__last_name__iexact=last_name
                ).first()

    return student


# ==========================================
# ATTENDANCE IMAGE UPLOAD AND EXTRACTION
# ==========================================

@login_required
def upload_attendance(request):

    form = AttendanceImageForm()
    entry_formset = None
    extracted_data = None
    error = None
    skipped_count = 0

    if request.method == "POST":

        form = AttendanceImageForm(request.POST, request.FILES)

        if form.is_valid():

            try:

                image = form.cleaned_data["attendance_image"]

                extracted_data = extract_attendance_data(image)

                logger.info(
                    "Attendance image extraction completed."
                )

                initial_data = []

                for record in extracted_data.get("records", []):

                    student_id = record.get("student_id")
                    student_name = record.get("student_name")

                    # Find student using ID or name
                    student = find_student(
                        student_id=student_id,
                        student_name=student_name
                    )

                    # Skip if student does not exist
                    if not student:

                        skipped_count += 1

                        logger.warning(
                            "Student not matched: ID=%s, Name=%s",
                            student_id,
                            student_name
                        )

                        continue

                    # Normalize attendance status
                    status = record.get("status")

                    if isinstance(status, str):
                        status = status.strip().capitalize()

                    if status not in ("Present", "Absent", "Late"):
                        status = ""

                    initial_data.append({
                        "student": student,
                        "date": extracted_data.get("date") or "",
                        "status": status,
                        "remarks": record.get("remarks") or "",
                    })

                # Create formset for matched students
                if initial_data:

                    entry_formset = AttendanceEntryFormSet(
                        initial=initial_data
                    )

                else:

                    error = (
                        "No matching students found in the database. "
                        "Please check Student IDs and student names."
                    )

            except Exception:
                logger.exception("Attendance extraction error")

                error = (
                    "Unable to extract attendance. "
                    "Please check the image and try again."
                )

        else:

            error = "Please upload a valid attendance image."

    return render(
        request,
        "ai_assistant/upload_attendance.html",
        {
            "form": form,
            "extracted_data": extracted_data,
            "entry_formset": entry_formset,
            "error": error,
            "skipped_count": skipped_count,
        }
    )


# ==========================================
# SAVE / UPDATE ATTENDANCE
# ==========================================

@login_required
def save_attendance(request):

    if request.method == "POST":

        formset = AttendanceEntryFormSet(request.POST)

        if formset.is_valid():

            created_count = 0
            updated_count = 0
            seen_records = set()

            try:

                with transaction.atomic():

                    for entry_form in formset:

                        student = entry_form.cleaned_data["student"]
                        attendance_date = entry_form.cleaned_data["date"]
                        status = entry_form.cleaned_data["status"]
                        remarks = entry_form.cleaned_data["remarks"]

                        # Prevent duplicate rows in same submission
                        key = (student.pk, attendance_date)

                        if key in seen_records:
                            raise ValueError(
                                f"Duplicate attendance submitted for "
                                f"{student.student_id} on {attendance_date}."
                            )

                        seen_records.add(key)

                        # Create new or update existing attendance
                        attendance, created = Attendance.objects.update_or_create(
                            student=student,
                            date=attendance_date,
                            defaults={
                                "status": status,
                                "remarks": remarks,
                            }
                        )

                        if created:
                            created_count += 1
                        else:
                            updated_count += 1

                return render(
                    request,
                    "ai_assistant/upload_attendance.html",
                    {
                        "form": AttendanceImageForm(),
                        "success_message": (
                            f"Attendance saved successfully! "
                            f"{created_count} new records created and "
                            f"{updated_count} existing records updated."
                        ),
                    }
                )

            except ValueError as e:

                return render(
                    request,
                    "ai_assistant/upload_attendance.html",
                    {
                        "form": AttendanceImageForm(),
                        "entry_formset": formset,
                        "error": str(e),
                    }
                )

            except IntegrityError:
                logger.exception("Attendance database integrity error")

                return render(
                    request,
                    "ai_assistant/upload_attendance.html",
                    {
                        "form": AttendanceImageForm(),
                        "entry_formset": formset,
                        "error": (
                            "A database conflict occurred while saving "
                            "attendance. Please try again."
                        ),
                    }
                )

            except Exception:
                logger.exception("Unexpected attendance saving error")

                return render(
                    request,
                    "ai_assistant/upload_attendance.html",
                    {
                        "form": AttendanceImageForm(),
                        "entry_formset": formset,
                        "error": (
                            "Unable to save attendance. "
                            "Please check the details and try again."
                        ),
                    }
                )

        else:

            logger.warning(
                "Attendance form errors: %s",
                formset.errors
            )

            logger.warning(
                "Attendance non-form errors: %s",
                formset.non_form_errors()
            )

            return render(
                request,
                "ai_assistant/upload_attendance.html",
                {
                    "form": AttendanceImageForm(),
                    "entry_formset": formset,
                    "error": "Please correct the errors in the attendance form.",
                }
            )

    return render(
        request,
        "ai_assistant/upload_attendance.html",
        {
            "form": AttendanceImageForm(),
            "error": "Invalid request.",
        }
    )
