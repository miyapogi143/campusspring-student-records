from django import forms

from .models import Course, Enrollment, Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "student_number",
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "contact_number",
            "birth_date",
            "program",
            "year_level",
            "section",
            "status",
        ]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["code", "title", "units", "instructor", "description", "is_active"]


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = [
            "student",
            "course",
            "school_year",
            "semester",
            "prelim_grade",
            "midterm_grade",
            "final_grade",
        ]


for form_class in (StudentForm, CourseForm, EnrollmentForm):
    for field in form_class.base_fields.values():
        field.widget.attrs.setdefault(
            "class",
            "form-check-input" if isinstance(field.widget, forms.CheckboxInput) else "form-control",
        )
