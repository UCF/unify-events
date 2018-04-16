import logging
import simplejson as json
import urllib

from django.conf import settings
from django.core.management.base import BaseCommand

from events.models import Location


#logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):
    def handle(self, *args, **options):
        locations_feed_url = 'https://' + settings.MAPS_DOMAIN + settings.LOCATION_DATA_URL
        data_file = urllib.urlopen(locations_feed_url)
        data = json.load(data_file)

        self.create_locations(data)

        data_file.close()

    def create_locations(self, data):
        """
        Create locations based on provided json data.
        Locations saved do not include their respective organizations.
        All imported events should be accepted as reviewed, correct data.
        """
        total_objects = len(data)
        parsed_objects = 0

        for object in data:
            # Get location title. 'name' val is available to all objects, but Building 'title'
            # and RegionalCampus 'description' are more descriptive. Use them if available.
            if hasattr(object, 'title'):
                title = object['title']
            elif hasattr(object, 'description'):
                title = object['description']
            else:
                title = object['name']

            # Get other data.
            mapurl = object['profile_link']
            import_id = object['id']

            if title:
                # Check to see if the location name, map url are too long
                if len(title) > 256:
                    title = title[0:256]
                if len(mapurl) > 400:
                    mapurl = mapurl[0:400]
                if len(import_id) > 256:
                    import_id = import_id[0:256]

                # See if an existing location exists with the current object ID.
                # Update the existing location if it exists; else, save the new location
                try:
                    old_location = Location.objects.get(import_id=import_id)
                except Exception, e:
                    logging.debug('No existing location found for %s: %s. Creating new location...' % (title, e))
                    # No existing matches found, or the matches were duplicate
                    new_location = Location(title=title, url=mapurl, room='', import_id=import_id, reviewed=True)
                    try:
                        new_location.save()
                    except Exception, e:
                        logging.error('Unable to save new location %s: %s' % (title, str(e)))
                    else:
                        parsed_objects += 1
                        logging.info('New location %s created.' % title)
                else:
                    logging.debug('Existing location %s found with Import ID %s. Updating existing location...' % (title, import_id))
                    old_location.title = title
                    old_location.url = mapurl
                    old_location.room = ''
                    old_location.reviewed = True
                    try:
                        old_location.save()
                    except Exception, e:
                        logging.error('Unable to save existing location %s: %s' % (title, str(e)))
                    else:
                        parsed_objects += 1
                        logging.info('Existing location %s with Import ID %s updated.' % (title, import_id))

        logging.info('Done. %s of %s available objects successfully imported.' % (parsed_objects, total_objects))
