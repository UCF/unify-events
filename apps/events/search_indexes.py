from datetime import datetime

from haystack import indexes
from events.models import Calendar
from events.models import State
from events.models import Event
from events.models import EventInstance


"""
Each SearchIndex class uses one 'text' field, which contains a string
of all searchable terms/phrases for each object.  This string is generated in
templates/search/indexes/events/ in a [modelname]_text.txt file.
The 'text' naming convention must be consistent throughout all classes.

All other fields exist for filtering purposes.  Currently, only the 'created_from'
field is used for filtering in this app; other fields are available for debugging.
"""

class EventIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    calendar = indexes.CharField(model_attr='calendar')
    category = indexes.CharField(model_attr='category')
    tags = indexes.MultiValueField()
    created_from = indexes.CharField(model_attr='created_from', default='None')

    def get_model(self):
        return Event

    def prepare_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]

    def get_filtered_event_queryset(self):
        """
        Only retrieve published events that are not archived
        (no pending events; allow canceled.)
        """
        now = datetime.now()
        unarchived_event_pks = EventInstance.objects.filter(end__gte=now, event__state__in=State.get_published_states()).values('event__pk')
        published_events = self.get_model().objects.filter(pk__in=unarchived_event_pks)

        return published_events

    def index_queryset(self, using=None):
        """
        Used when the entire index for model is updated.
        """
        return self.get_filtered_event_queryset()

    def read_queryset(self, using=None):
        """
        Get the default QuerySet for read actions.
        """
        return self.get_filtered_event_queryset()

    def build_queryset(self, using=None, start_date=None, end_date=None):
        """
        Get the default QuerySet to index when doing an index update.
        """
        return self.get_filtered_event_queryset()

    def load_all_queryset(self):
        """
        Provides the ability to override how objects get loaded
        in conjunction with `RelatedSearchQuerySet.load_all`.
        """
        return self.get_filtered_event_queryset()


class CalendarIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    created_from = indexes.CharField(default='None') # Necessary for GlobalSearchView when fetching original events

    def get_model(self):
        return Calendar

    def index_queryset(self, using=None):
        """
        Used when the entire index for model is updated.
        Retrieve all calendars.
        """
        return self.get_model().objects.all()
