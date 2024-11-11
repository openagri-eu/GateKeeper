import os
from io import StringIO

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.recorder import MigrationRecorder
from django.contrib.auth import get_user_model


# Make sure migrations folder inside backend app contains an empty __init__.py file


class Command(BaseCommand):
    help = "Initial setup command"

    def check_pending_migrations(self):
        for connection in connections.all():
            executor = MigrationExecutor(connection)
            targets = executor.loader.graph.leaf_nodes()
            recorder = MigrationRecorder(connection)
            applied = recorder.applied_migrations()

            unapplied = [migration for migration in targets if migration not in applied]

            return len(unapplied) > 0

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Checking for migration changes...'))

        if self.check_pending_migrations():
            self.stdout.write(self.style.SUCCESS('Pending migrations detected, running migrations...'))
            call_command('migrate')


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