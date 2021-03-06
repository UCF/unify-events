import csv
from io import StringIO

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db.models import Q

from events.models import Calendar

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'audit',
            type=str,
            help='The audit to run. Choices are: empty-calendars, invalid-names and pii-in-title'
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
        elif self.audit_to_run == 'pii-in-title':
            self.pii_in_titles()
        else:
            raise CommandError(f"{self.audit_to_run} is not a valid audit.")

    def empty_calendars(self):
        inactive = Calendar.objects.without_recent_events()
        output = []

        for cal in inactive:
            output.append({
                'id': cal.id,
                'title': cal.title,
                'owner_name': cal.owner.get_full_name() if cal.owner else None,
                'owner_email': cal.owner.email if cal.owner else None
            })

        fieldnames = ['id', 'title', 'owner_name', 'owner_email']

        if self.file:
            with open(self.file, 'w') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

                writer.writeheader()

                for row in output:
                    writer.writerow(row)

                # Only print stats if we're spitting out a file
                stats = f"""
Inactive Calendars Found: {inactive.count()}
CSV File exported to: {self.file if self.file else 'Not Exported'}
        """

                print(stats)
        else:
            with StringIO() as stringio:
                writer = csv.DictWriter(stringio, fieldnames=fieldnames)

                writer.writeheader()

                for row in output:
                    writer.writerow(row)

                print(stringio.getvalue())

    def invalid_names(self):
        invalid = Calendar.objects.invalid_named_calendars()
        output = []

        for cal in invalid:
            output.append({
                'id': cal.id,
                'title': cal.title,
                'owner_name': cal.owner.get_full_name() if cal.owner else None,
                'owner_email': cal.owner.email if cal.owner else None
            })

        fieldnames = ['id', 'title', 'owner_name', 'owner_email']

        if self.file:
            with open(self.file, 'w') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

                writer.writeheader()

                for row in output:
                    writer.writerow(row)

                # Only print stats if we're spitting out a file
                stats = f"""
Invalid Calendar Names Found: {invalid.count()}
CSV File exported to: {self.file if self.file else 'Not Exported'}
        """

                print(stats)
        else:
            with StringIO() as stringio:
                writer = csv.DictWriter(stringio, fieldnames=fieldnames)
                writer.writeheader()

                for row in output:
                    writer.writerow(row)

                print(stringio.getvalue())

    def pii_in_titles(self):
        usernames = [x.username for x in User.objects.all()]
        query = Q()

        for username in usernames:
            query = query | Q(title__istartswith=username.lower())

        invalid = Calendar.objects.filter(query)

        output = []

        for cal in invalid:
            output.append({
                'id': cal.id,
                'title': cal.title,
                'owner_name': cal.owner.get_full_name() if cal.owner else None,
                'owner_email': cal.owner.email if cal.owner else None
            })

        fieldnames = ['id', 'title', 'owner_name', 'owner_email']

        if self.file:
            with open(self.file, 'w') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

                writer.writeheader()

                for row in output:
                    writer.writerow(row)

                stats = f"""
Invalid Calendar Names Found: {invalid.count()}
CSV File exported to: {self.file if self.file else 'Not Exported'}
        """

                print(stats)
        else:
            with StringIO() as stringio:
                writer = csv.DictWriter(stringio, fieldnames=fieldnames)
                writer.writeheader()

                for row in output:
                    writer.writerow(row)

                print(stringio.getvalue())
