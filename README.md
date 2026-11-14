# CampusSpring

A standalone student records system for academic staff, built with Django. CampusSpring provides a student dashboard, searchable directories, course registration and grading, and CSV export.

## Features

- Staff-only authentication and record management
- Student profiles, statuses, and academic year/section
- Course catalog with active/inactive state
- Enrollment records for school year and semester
- Prelim, midterm, and final grades with a computed average
- Search across students, courses, and enrollments
- Student CSV export
- Responsive dashboard and interface

## Run locally

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. Sign in with the staff account created above. SQLite is used by default; setting `DATABASE_URL` enables a managed PostgreSQL database.

## Deploy to Render

The included `render.yaml` creates an independent free web service with auto-deploy enabled. This service uses SQLite on Render's filesystem; its records are not durable and may be lost when the service restarts or redeploys. Use PostgreSQL for persistent records.

Connect this repository as a new Render Blueprint; do not attach it to another records service. To provision the initial staff account, set `BOOTSTRAP_ADMIN_USERNAME` and `BOOTSTRAP_ADMIN_PASSWORD` in this Render service's environment before deploying. Keep those credentials in Render (never in Git) so the account can be recreated after a redeploy. For persistent records and one-time credential handling, use PostgreSQL.
