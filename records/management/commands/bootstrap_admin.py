import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create the initial staff superuser from deployment environment variables."

    def handle(self, *args, **options):
        username = os.environ.get("BOOTSTRAP_ADMIN_USERNAME")
        password = os.environ.get("BOOTSTRAP_ADMIN_PASSWORD")
        if not username and not password:
            self.stdout.write("No bootstrap admin credentials provided; skipping.")
            return
        if not username or not password:
            raise CommandError("Set both BOOTSTRAP_ADMIN_USERNAME and BOOTSTRAP_ADMIN_PASSWORD.")

        user_model = get_user_model()
        if user_model.objects.filter(username=username).exists():
            self.stdout.write(f"Staff account {username!r} already exists; leaving it unchanged.")
            return
        user_model.objects.create_superuser(username=username, password=password)
        self.stdout.write(self.style.SUCCESS(f"Created staff account {username!r}."))
