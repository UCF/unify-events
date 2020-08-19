from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from django.db.migrations.recorder import MigrationRecorder
from django.db import connection

class Command(BaseCommand):
    help = 'Runs deployment related tasks.'

    def handle(self, *args, **options):
        # Get all the table names
        all_tables = connection.introspection.table_names()

        # Check to see if the django_migrations table exists
        if 'django_migrations' not in all_tables:
            # The showmigrations command will create the migration table if it doesn't exist
            call_command('showmigrations')
            self.stdout.write("Create migration table")

        # Get a count of migrations
        migration_count = MigrationRecorder.Migration.objects.filter(applied__isnull=False).count()

        # If there are no migrations, but the events table exists, this is an existing installation
        if migration_count == 0 and 'events_event' in all_tables:
            call_command('migrate', '--fake-initial')
            self.stdout.write("Running initial migrations")
        else:
            # Run thr normal migration is all other instances
            call_command('migrate')
            self.stdout.write("Running migrations")

        # Collect static files
        call_command('collectstatic', '--link', '--no-input')

        self.stdout.write(self.style.SUCCESS("Finished deploying"))

