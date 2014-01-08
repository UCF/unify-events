from haystack import indexes
from events.models import State
from events.models import Event

class EventIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    calendar = indexes.CharField(model_attr='calendar')
    title = indexes.CharField(model_attr='title')
    description = indexes.CharField(model_attr='description')
    category = indexes.CharField(model_attr='category')
    tags = indexes.CharField(model_attr='tags')

    def get_model(self):
        return Event

    def index_queryset(self, using=None):
        """
        Used when the entire index for model is updated.
        Only retrieve published events that are published
        (no pending or rereview events; allow canceled.)
        """
        return self.get_model().objects.filter(state=State.posted)
