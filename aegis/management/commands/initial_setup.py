import os
from io import StringIO

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


# Make sure migrations folder inside backend app contains an empty __init__.py file


class Command(BaseCommand):
    help = "Initial setup command"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Checking for migration changes...'))

        # Capture output of makemigrations to determine if changes were made
        out = StringIO()
        call_command('makemigrations', stdout=out)
        output = out.getvalue()

        if 'No changes detected' not in output:
            self.stdout.write(self.style.SUCCESS('Changes detected, running migrations...'))
            call_command('migrate')
        else:
            self.stdout.write(self.style.SUCCESS('No changes detected.'))

        self.stdout.write(self.style.SUCCESS('Collecting static files...'))
        call_command('collectstatic', '--noinput')

        self.stdout.write(self.style.SUCCESS('Checking for superuser...'))
        user = get_user_model()

        superuser_username = os.getenv('SUPERUSER_USERNAME', 'pranav')
        superuser_email = os.getenv('SUPERUSER_EMAIL', 'p.bapat@maastrichtuniversity.nl')
        superuser_password = os.getenv('SUPERUSER_PASSWORD', '/i4KNmz/?_x@(Nb')

        if not user.objects.filter(username=superuser_username).exists():
            self.stdout.write(self.style.WARNING('Superuser does not exist. Creating one...'))
            user.objects.create_superuser(
                username=superuser_username,
                email=superuser_email,
                password=superuser_password
            )
            self.stdout.write(self.style.SUCCESS('Superuser successfully created.'))
        else:
            self.stdout.write(self.style.SUCCESS('Superuser already exists.'))
