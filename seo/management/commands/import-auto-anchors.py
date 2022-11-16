import settings
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError

from seo.models import AutoAnchor

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
            default='https://search.cm.ucf.edu/api/v1'
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
        self.search_service_base_url = options.get('searech_service_api', None)
        self.api_key = options.get('api_key', None)
        self.update_date = datetime.now()
        self.remove_stale = options.get('remove_stale', False)

        self.patterns_created = 0
        self.patterns_updated = 0
        self.patterns_deleted = 0

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
        request_url = f"{self.search_service_base_url}/seo/patterns"

        while request_url:
            response = requests.get(request_url, params=params)
            if response.ok:
                resp_data = response.json()
                request_url = resp_data['next']

                ret_val.extend(resp_data['results'])

        return ret_val


    def __process_results(self):
        """
        Processes the auto anchors
        """
        for result in self.auto_anchors:
            self.__add_or_update_auto_anchor(result)


    def __add_or_update_auto_anchor(self, data):
        """
        Adds or updates an auto anchor
        """
        try:
            auto_anchor = AutoAnchor.objects.get(pattern__iexact=data['pattern'], imported=True)
            auto_anchor.url = data['url']
            auto_anchor.updated_on = self.update_date
            auto_anchor.save()
            self.patterns_updated += 1
        except AutoAnchor.DoesNotExist:
            auto_anchor = AutoAnchor(
                pattern = data['pattern'],
                url=data['url'],
                created_on=self.update_date,
                updated_on=self.update_date,
                imported=True
            )
            auto_anchor.save()
            self.patterns_created += 1


    def __remove_stale(self):
        """
        Removes any imported auto anchors that were not in the results
        from the search service
        """
        patterns = AutoAnchor.objects.filter(imported=True, updated_at__lt=self.update_date)
        self.patterns_deleted = patterns.count()

        if self.patterns_deleted > 0:
            patterns.delete()

    def __report_results(self):
        """
        Writes the results of the import to the screen
        """
        self.stdout.writelines([
            "All done!\n",
            f"Patterns created: {self.patterns_created}",
            f"Patterns updated: {self.patterns_updated}",
            f"Patterns deleted: {self.patterns_deleted}\n"
        ])