import argparse
import csv
import os

from django.core.management.base import BaseCommand, CommandError

from taggit.models import Tag

class Command(BaseCommand):
    def add_arguments(self, parser):
        """
        Handles adding the command line arguments
        for the command.
        """
        parser.add_argument(
            'tag_file',
            type=argparse.FileType('r'),
            help='Path to the CSV file with the tags to be removed.'
        )

        parser.add_argument(
            '--tag-id-fieldname',
            dest='tag_id_fieldname',
            type=str,
            default='Tag ID',
            help='The name of the field in the CSV for the Tag ID field.'
        )

        parser.add_argument(
            '--assoc',
            dest='assoc',
            action='store_true',
            help='Looks for a related_tag field within the CSV and associates tags based on the values provided. This option has not yet been implemented.'
        )

        parser.add_argument(
            '--assoc-fieldname',
            dest='assoc_fieldname',
            type=str,
            default='Assoc',
            help='The name of the field in the CSV for the associated tag field. The --assoc option has not yet been implemented.'
        )

        parser.add_argument(
            '--trial-run',
            dest='trial_run',
            action='store_true',
            help='Causes the command not be run but gives a preview of the outcome.'
        )


    def handle(self, *args, **options):
        """
        The entry point for execution of the command.
        """
        self.tags_to_process = {}

        csvfile = options['tag_file']
        self.trial = options['trial_run']
        self.assoc = options['assoc']
        self.tag_id_fieldname = options['tag_id_fieldname']
        self.assoc_fieldname = options['assoc_fieldname']

        # Setup our stat variables
        self.tags_processed = 0
        self.tags_found = 0
        self.tags_not_found = 0
        self.valid_assocs = 0
        self.invalid_assocs = 0
        self.tags_removed = 0

        if self.assoc:
            raise NotImplementedError('The --assoc option has not been implemented at this time.')

        self.parse_file(csvfile)
        self.process_tags()
        self.print_stats()


    def print_stats(self):
        stats = f"""
Tags Processed: {self.tags_processed}
Tags Found    : {self.tags_found}
Tags Not Found: {self.tags_not_found}
        """

        assocs = f"""
Valid Associations  : {self.valid_assocs}
Invalid Associations: {self.invalid_assocs}
        """

        removed = f"""
Tags Removed  : {self.tags_removed}
        """

        if self.trial:
            self.stdout.write("THIS WAS A TRIAL RUN")

        self.stdout.write(stats)
        if self.assoc:
            self.stdout.write(assocs)
        else:
            self.stdout.write(removed)

    def parse_file(self, csvfile):
        """
        Helper function that parses the CSV file
        and sets the tags_to_process dictionary.
        """
        reader = csv.DictReader(csvfile)

        for line in reader:
            tag_id = None
            assoc = None

            try:
                tag_id = int(line[self.tag_id_fieldname])
            except KeyError:
                self.stderr.write(f'The fieldname {self.tag_id_fieldname} is not present in this CSV.')
            except ValueError:
                self.stderr.write(f'The value {line[self.tag_id_fieldname]} is not a valid integer.')

            if self.assoc:
                try:
                    assoc = int(line[self.assoc_fieldname])
                except KeyError:
                    self.stderr.write(f'The fieldname {self.assoc_fieldname} is not present in this CSV.')
                except ValueError:
                    self.stderr.write(f'The value {line[self.assoc_fieldname]} is not a valid integer.')

            self.tags_to_process[tag_id] = {
                'tag_id': tag_id,
                'assoc': assoc
            }


    def process_tags(self):
        """
        Function that loops through the tags to be processed
        and processes them!
        """
        for tag_info in self.tags_to_process.values():
            # If the tag id isn't set, move along.
            if tag_info['tag_id'] == None:
                self.tags_not_found += 1
                continue

            try:
                tag = Tag.objects.get(pk=tag_info['tag_id'])
                self.tags_found += 1
            except Tag.DoesNotExist:
                self.tags_not_found += 1
                continue

            if self.assoc and tag_info['assoc'] is not None:
                try:
                    assoc_tag = Tag.objects.get(pk=tag_info['assoc'])
                    self.valid_assocs += 1
                except Tag.DoesNotExist:
                    self.invalid_assocs += 1
                    continue

            # If we're not associating tags, we're removing them
            if not self.assoc and not self.trial:
                tag.delete()
                self.tags_removed += 1

    def associate_tags(self, original_tag, associated_tag):
        """
        Function for associating tags. For right now, this does nothing.
        """
        if self.trial:
            return

        return
