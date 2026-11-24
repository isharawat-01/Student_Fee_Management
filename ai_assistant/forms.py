
from datetime import date

from django import forms
from django.forms import formset_factory, BaseFormSet
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

from timetable.models import Timetable
from attendance.models import Attendance


# ==========================================
# TIMETABLE IMAGE FORM
# ==========================================

class TimetableImageForm(forms.Form):

    timetable_image = forms.ImageField(
        label="Upload Timetable Image",
        help_text="Upload a clear timetable image (JPG, JPEG or PNG).",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png"]
            )
        ]
    )


# ==========================================
# TIMETABLE ENTRY FORM
# ==========================================

class TimetableEntryForm(forms.ModelForm):

    class Meta:
        model = Timetable

        fields = [
            "course_subject",
            "employee",
            "day",
            "start_time",
            "end_time",
            "room_number",
        ]

        widgets = {
            "start_time": forms.TimeInput(
                attrs={"type": "time"}
            ),
            "end_time": forms.TimeInput(
                attrs={"type": "time"}
            ),
        }

    def clean(self):

        cleaned_data = super().clean()

        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time and end_time <= start_time:

            raise ValidationError(
                "End time must be later than start time."
            )

        return cleaned_data


TimetableEntryFormSet = formset_factory(
    TimetableEntryForm,
    extra=0
)


# ==========================================
# ATTENDANCE IMAGE FORM
# ==========================================

class AttendanceImageForm(forms.Form):

    attendance_image = forms.ImageField(
        label="Upload Attendance Register Image",
        help_text="Upload a clear attendance register image (JPG, JPEG or PNG).",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png"]
            )
        ]
    )


# ==========================================
# ATTENDANCE ENTRY FORM
# ==========================================

class AttendanceEntryForm(forms.ModelForm):

    class Meta:
        model = Attendance

        fields = [
            "student",
            "date",
            "status",
            "remarks",
        ]

        widgets = {
            "date": forms.DateInput(
                attrs={"type": "date"}
            ),
        }

    # Prevent future attendance dates
    def clean_date(self):

        attendance_date = self.cleaned_data.get("date")

        if attendance_date and attendance_date > date.today():

            raise ValidationError(
                "Attendance date cannot be in the future."
            )

        return attendance_date

    # Existing student-date records can be updated
    def validate_unique(self):
        pass


# ==========================================
# ATTENDANCE FORMSET VALIDATION
# ==========================================

class AttendanceBaseFormSet(BaseFormSet):

    def clean(self):

        super().clean()

        if any(self.errors):
            return

        seen_records = set()

        for form in self.forms:

            if not hasattr(form, "cleaned_data"):
                continue

            if not form.cleaned_data:
                continue

            student = form.cleaned_data.get("student")
            attendance_date = form.cleaned_data.get("date")

            if student and attendance_date:

                key = (student.pk, attendance_date)

                if key in seen_records:

                    raise ValidationError(
                        "Duplicate attendance found for the same student and date."
                    )

                seen_records.add(key)


AttendanceEntryFormSet = formset_factory(
    AttendanceEntryForm,
    formset=AttendanceBaseFormSet,
    extra=0
)
