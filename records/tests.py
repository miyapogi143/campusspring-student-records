from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Course, Enrollment, Student


class EnrollmentAverageTests(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            student_number="2026-001",
            first_name="Alex",
            last_name="Rivera",
            email="alex@example.com",
        )
        self.course = Course.objects.create(code="IT101", title="Foundations of IT")

    def test_average_uses_only_entered_grades(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            school_year="2026-2027",
            prelim_grade=80,
            final_grade=90,
        )
        self.assertEqual(enrollment.average, 85)

    def test_average_is_empty_when_no_grades_exist(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            school_year="2026-2027",
        )
        self.assertIsNone(enrollment.average)


class StaffWorkflowTests(TestCase):
    def setUp(self):
        self.staff = get_user_model().objects.create_user(
            username="registrar", password="safe-test-password", is_staff=True
        )
        self.client.force_login(self.staff)

    def test_dashboard_shows_empty_state_and_loads(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "New students")

    def test_student_search_matches_student_number(self):
        Student.objects.create(
            student_number="2026-224",
            first_name="Sam",
            last_name="Lee",
            email="sam@example.com",
        )
        response = self.client.get(reverse("student_list"), {"q": "2026-224"})
        self.assertContains(response, "Sam Lee")

    def test_delete_requires_post(self):
        student = Student.objects.create(
            student_number="2026-225",
            first_name="Taylor",
            last_name="Kim",
            email="taylor@example.com",
        )
        response = self.client.get(reverse("student_delete", args=[student.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Student.objects.filter(pk=student.pk).exists())
        response = self.client.post(reverse("student_delete", args=[student.pk]))
        self.assertRedirects(response, reverse("student_list"))
        self.assertFalse(Student.objects.filter(pk=student.pk).exists())

    def test_export_is_staff_only_csv(self):
        response = self.client.get(reverse("export_students_csv"))
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("Student Number", response.content.decode())

    def test_staff_record_pages_render(self):
        student = Student.objects.create(
            student_number="2026-226",
            first_name="Morgan",
            last_name="Park",
            email="morgan@example.com",
        )
        course = Course.objects.create(code="IT102", title="Data Concepts")
        enrollment = Enrollment.objects.create(
            student=student, course=course, school_year="2026-2027"
        )
        routes = (
            reverse("student_detail", args=[student.pk]),
            reverse("student_create"),
            reverse("student_edit", args=[student.pk]),
            reverse("course_list"),
            reverse("course_create"),
            reverse("course_edit", args=[course.pk]),
            reverse("course_delete", args=[course.pk]),
            reverse("enrollment_list"),
            reverse("enrollment_create"),
            reverse("enrollment_edit", args=[enrollment.pk]),
            reverse("enrollment_delete", args=[enrollment.pk]),
        )
        for route in routes:
            with self.subTest(route=route):
                self.assertEqual(self.client.get(route).status_code, 200)

    def test_dashboard_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(response, f"{reverse('login')}?next=/")
