from datetime import datetime

from haystack import indexes
from events.models import Calendar
from events.models import State
from events.models import Event
from events.models import EventInstance


class EventIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    calendar = indexes.CharField(model_attr='calendar')
    description = indexes.CharField(model_attr='description')
    category = indexes.CharField(model_attr='category')
    tags = indexes.CharField(model_attr='tags')

    def get_model(self):
        return Event

    def index_queryset(self, using=None):
        """
        Used when the entire index for model is updated.
        Only retrieve posted events that are not archived
        (no pending or rereview events; allow canceled.)
        """
        now = datetime.now()
        unarchived_event_pks = EventInstance.objects.filter(end__gte=now, event__state=State.posted).values('event__pk')
        published_events = self.get_model().objects.filter(pk__in=unarchived_event_pks)

        return published_events


class CalendarIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    description = indexes.CharField(model_attr='description', null=True)

    def get_model(self):
        return Calendar

    def index_queryset(self, using=None):
        """
        Used when the entire index for model is updated.
        Retrieve all calendars.
        """
        return self.get_model().objects.all()