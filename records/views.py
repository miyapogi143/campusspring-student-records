import csv

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CourseForm, EnrollmentForm, StudentForm
from .models import Course, Enrollment, Student


def staff_required(view):
    return staff_member_required(view, login_url="login")


@staff_required
def dashboard(request):
    context = {
        "student_count": Student.objects.count(),
        "active_count": Student.objects.filter(status="Active").count(),
        "course_count": Course.objects.filter(is_active=True).count(),
        "enrollment_count": Enrollment.objects.count(),
        "recent_students": Student.objects.order_by("-created_at")[:6],
        "recent_enrollments": Enrollment.objects.select_related("student", "course")[:6],
        "popular_courses": Course.objects.annotate(
            enrollment_count=Count("enrollments")
        ).order_by("-enrollment_count", "code")[:5],
    }
    return render(request, "records/dashboard.html", context)


@staff_required
def student_list(request):
    query = request.GET.get("q", "").strip()
    students = Student.objects.all()
    if query:
        students = students.filter(
            Q(student_number__icontains=query)
            | Q(first_name__icontains=query)
            | Q(middle_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(email__icontains=query)
            | Q(program__icontains=query)
        )
    return render(request, "records/student_list.html", {"students": students, "q": query})


@staff_required
def student_create(request):
    form = StudentForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Student record added.")
        return redirect("student_list")
    return render(request, "records/form.html", {"form": form, "heading": "Add student", "back_url": "student_list"})


@staff_required
def student_edit(request, pk):
    student = get_object_or_404(Student, pk=pk)
    form = StudentForm(request.POST or None, instance=student)
    if form.is_valid():
        form.save()
        messages.success(request, "Student record updated.")
        return redirect("student_detail", pk=student.pk)
    return render(request, "records/form.html", {"form": form, "heading": "Edit student", "back_url": "student_list"})


@staff_required
def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    enrollments = student.enrollments.select_related("course")
    return render(request, "records/student_detail.html", {"student": student, "enrollments": enrollments})


@staff_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        student.delete()
        messages.success(request, "Student record deleted.")
        return redirect("student_list")
    return render(request, "records/confirm_delete.html", {"object": student, "back_url": "student_list", "delete_url": "student_delete"})


@staff_required
def course_list(request):
    query = request.GET.get("q", "").strip()
    courses = Course.objects.annotate(enrollment_count=Count("enrollments"))
    if query:
        courses = courses.filter(
            Q(code__icontains=query)
            | Q(title__icontains=query)
            | Q(instructor__icontains=query)
        )
    return render(request, "records/course_list.html", {"courses": courses, "q": query})


@staff_required
def course_create(request):
    form = CourseForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Course added.")
        return redirect("course_list")
    return render(request, "records/form.html", {"form": form, "heading": "Add course", "back_url": "course_list"})


@staff_required
def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)
    form = CourseForm(request.POST or None, instance=course)
    if form.is_valid():
        form.save()
        messages.success(request, "Course updated.")
        return redirect("course_list")
    return render(request, "records/form.html", {"form": form, "heading": "Edit course", "back_url": "course_list"})


@staff_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == "POST":
        if course.enrollments.exists():
            course.is_active = False
            course.save(update_fields=["is_active"])
            messages.info(request, "Course has enrollments, so it was deactivated instead.")
        else:
            course.delete()
            messages.success(request, "Course deleted.")
        return redirect("course_list")
    return render(
        request,
        "records/confirm_delete.html",
        {
            "object": course,
            "back_url": "course_list",
            "delete_url": "course_delete",
            "has_enrollments": course.enrollments.exists(),
        },
    )


@staff_required
def enrollment_list(request):
    query = request.GET.get("q", "").strip()
    enrollments = Enrollment.objects.select_related("student", "course")
    if query:
        enrollments = enrollments.filter(
            Q(student__student_number__icontains=query)
            | Q(student__first_name__icontains=query)
            | Q(student__last_name__icontains=query)
            | Q(course__code__icontains=query)
            | Q(course__title__icontains=query)
        )
    return render(request, "records/enrollment_list.html", {"enrollments": enrollments, "q": query})


@staff_required
def enrollment_create(request):
    form = EnrollmentForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Enrollment created.")
        return redirect("enrollment_list")
    return render(request, "records/form.html", {"form": form, "heading": "New enrollment and grades", "back_url": "enrollment_list"})


@staff_required
def enrollment_edit(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    form = EnrollmentForm(request.POST or None, instance=enrollment)
    if form.is_valid():
        form.save()
        messages.success(request, "Enrollment and grades updated.")
        return redirect("enrollment_list")
    return render(request, "records/form.html", {"form": form, "heading": "Update enrollment and grades", "back_url": "enrollment_list"})


@staff_required
def enrollment_delete(request, pk):
    enrollment = get_object_or_404(Enrollment, pk=pk)
    if request.method == "POST":
        enrollment.delete()
        messages.success(request, "Enrollment removed.")
        return redirect("enrollment_list")
    return render(request, "records/confirm_delete.html", {"object": enrollment, "back_url": "enrollment_list", "delete_url": "enrollment_delete"})


@staff_required
def export_students_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="student-records.csv"'
    writer = csv.writer(response)
    writer.writerow(
        ["Student Number", "First Name", "Middle Name", "Last Name", "Email", "Program", "Year", "Section", "Status"]
    )
    for student in Student.objects.all():
        writer.writerow(
            [
                student.student_number,
                student.first_name,
                student.middle_name,
                student.last_name,
                student.email,
                student.program,
                student.get_year_level_display(),
                student.section,
                student.status,
            ]
        )
    return response
