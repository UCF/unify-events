from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from django.db.migrations.recorder import MigrationRecorder
from django.db import connection

class Command(BaseCommand):
    help = 'Runs deployment related tasks.'

    def handle(self, *args, **options):
        migration_count = MigrationRecorder.Migration.objects.filter(applied__isnull=False).count()
        all_tables = connection.introspection.table_names()

        # Tables exists, but there are no migrations run
        if 'django_migrations' not in all_tables:
            call_command('migrate', '--fake-initial')
            self.stdout.write("Running initial migrations")
        elif migration_count == 0 and 'events_event' in all_tables:
            call_command('migrate', '--fake-initial')
            self.stdout.write("Running initial migrations")
        else:
            call_command('migrate')
            self.stdout.write("Running migrations")

        call_command('collectstatic', '--link', '--no-input')

        self.stdout.write(self.style.SUCCESS("Finished deploying"))

