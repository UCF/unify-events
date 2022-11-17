import settings
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError

from seo.models import InternalLink, KeywordPhrase

import requests

class Command(BaseCommand):
    help = 'Imports defined patterns from the search service'

    def add_arguments(self, parser) -> None:
        """
        Adds the arguments to the parser
        """
        parser.add_argument(
            '--search-service-api',
            type=str,
            dest='search_service_api',
            help='The base URL of the search service',
            default=None
        )

        parser.add_argument(
            '--api-key',
            dest='api_key',
            type=str,
            help='The API key to use when connecting to the search service',
            default=None
        )

        parser.add_argument(
            '--remove-stale',
            dest='remove_stale',
            action='store_true',
            default=False
        )

    def handle(self, *args, **options):
        """
        Entry point for the command
        """
        self.search_service_base_url = options.get('search_service_api', None)
        self.api_key = options.get('api_key', None)
        self.update_date = datetime.now()
        self.remove_stale = options.get('remove_stale', False)

        self.patterns_created = 0
        self.patterns_updated = 0
        self.patterns_deleted = 0
        self.patterns_skipped = 0

        if 'SEO_SEARCH_SERVICE_API' in settings.__dict__.keys() and not self.search_service_base_url:
            self.search_service_base_url = settings.SEO_SEARCH_SERVICE_API

        if 'SEO_SEARCH_SERVICE_API_KEY' in settings.__dict__.keys() and not self.api_key:
            self.api_key = settings.SEO_SEARCH_SERVICE_API_KEY

        if not self.search_service_base_url or not self.api_key:
            raise CommandError("A base URL must be set for the search service API and an API key must be provided.\nThese can be passed in as arguments or can be set in the settings_local.py file.")

        self.auto_anchors = self.__get_auto_anchors()
        self.__process_results()

        if self.remove_stale:
            self.__remove_stale()

        self.__report_results()

    def __get_auto_anchors(self) -> list:
        """
        Retrieves the auto anchors from the search service
        """
        ret_val = []
        params = {
            "key": self.api_key
        }
        request_url = f"{self.search_service_base_url}/seo/internal-links/"
        while request_url:
            response = requests.get(request_url, params=params)
            if response.ok:
                resp_data = response.json()
                request_url = resp_data['next']

                ret_val.extend(resp_data['results'])
            else:
                request_url = None

        return ret_val


    def __process_results(self):
        """
        Processes the auto anchors
        """
        for result in self.auto_anchors:
            self.__add_or_update_internal_link(result)


    def __add_or_update_internal_link(self, data):
        """
        Adds or updates an auto anchor
        """
        internal_link = None

        try:
            internal_link = InternalLink.objects.get(url__iexact=data['url'])

            # If this is a local auto anchor, move on
            if internal_link.local() == True:
                self.patterns_skipped += 1
                return

            internal_link.updated_on = self.update_date
            internal_link.save()
            self.patterns_updated += 1
        except InternalLink.DoesNotExist:
            internal_link = InternalLink(
                url=data['url'],
                created_on=self.update_date,
                updated_on=self.update_date,
                imported=True
            )
            internal_link.save()
            self.patterns_created += 1

        for phrase in data['phrases']:
            try:
                kwp = KeywordPhrase.objects.get(phrase=phrase)
                kwp.link = internal_link
                kwp.save()
            except KeywordPhrase.DoesNotExist:
                kwp = KeywordPhrase(phrase=phrase)
                kwp.link = internal_link
                kwp.save()


    def __remove_stale(self):
        """
        Removes any imported auto anchors that were not in the results
        from the search service
        """
        links = InternalLink.objects.filter(imported=True, updated_at__lt=self.update_date)
        self.patterns_deleted = links.count()

        if self.patterns_deleted > 0:
            links.delete()

    def __report_results(self):
        """
        Writes the results of the import to the screen
        """
        self.stdout.writelines([
            "All done!\n",
            f"Internal Links created: {self.patterns_created}",
            f"Internal Links updated: {self.patterns_updated}",
            f"Internal Links skipped: {self.patterns_skipped}",
            f"Internal Links deleted: {self.patterns_deleted}\n"
        ])
