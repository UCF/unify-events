import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from events.models import Calendar

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'audit',
            type=str,
            help='The audit to run. Choices are: empty-calendars and invalid-names'
        )

        parser.add_argument(
            '--output-file',
            type=str,
            dest='output_file',
            default=None
        )

    def handle(self, *args, **options):
        self.audit_to_run = options['audit']
        self.file = options['output_file']

        if self.audit_to_run == 'empty-calendars':
            self.empty_calendars()
        elif self.audit_to_run == 'invalid-names':
            self.invalid_names()
        else:
            raise CommandError(f"{self.audit_to_run} is not a valid audit.")

    def empty_calendars(self):
        inactive = Calendar.objects.inactive_calendars()
        output = []
        filepath = os.path.abspath(self.file)

        for cal in inactive:
            output.append({
                'title': cal.title,
                'owner_name': cal.owner.get_full_name() if cal.owner else None,
                'owner_email': cal.owner.email if cal.owner else None
            })

        with open(self.file, 'w') as csv_file:
            fieldnames = ['title', 'owner_name', 'owner_email']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()

            for row in output:
                writer.writerow(row)

        stats = f"""
Inactive Calendars Found: {inactive.count()}
CSV File exported to: {filepath}
        """

        print(stats)

    def invalid_names(self):
        invalid = Calendar.objects.invalid_named_calendars()
        output = []
        filepath = os.path.abspath(self.file)

        for cal in invalid:
            output.append({
                'title': cal.title,
                'owner_name': cal.owner.get_full_name() if cal.owner else None,
                'owner_email': cal.owner.email if cal.owner else None
            })

        with open(self.file, 'w') as csv_file:
            fieldnames = ['title', 'owner_name', 'owner_email']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()

            for row in output:
                writer.writerow(row)

                stats = f"""
Invalid Calendar Names Found: {inactive.count()}
CSV File exported to: {filepath}
        """

        print(stats)
