import logging

from haystack import signals
from haystack.exceptions import NotHandled

from django.db.models.signals import post_delete
from django.db.models.signals import post_save

from events.models.event import Event, State
from events.models.calendar import Calendar

log = logging.getLogger(__name__)


class CustomHaystackSignalProcessor(signals.BaseSignalProcessor):
    """
    A convenient way to attach Haystack to Django's signals & cause things to
    index.
    """

    def setup(self):
        """
        Listen for Events and Calendars.
        """
        post_save.connect(self.handle_save, sender=Event)
        post_delete.connect(self.handle_delete, sender=Event)
        post_save.connect(self.handle_save, sender=Calendar)
        post_delete.connect(self.handle_delete, sender=Calendar)

    def teardown(self):
        """
        Disconnect for Events and Calendars.
        """
        post_save.disconnect(self.handle_save, sender=Event)
        post_delete.disconnect(self.handle_delete, sender=Event)
        post_save.disconnect(self.handle_save, sender=Calendar)
        post_delete.disconnect(self.handle_delete, sender=Calendar)

    def handle_save(self, sender, instance, **kwargs):
        """
        Given an individual model instance, determine which backends the
        update should be sent to & update the object on those backends.

        Updated for this app to actually log an error on NotHandled (by
        default, BaseSignalProcessor just passes) and properly manage
        Event state changes.

        Args:
          sender   (obj): The model class to receive signals from.
          instance (obj): The model instance.
          **kwargs: Arbitrary keyword arguments.
        """
        using_backends = self.connection_router.for_write(instance=instance)
        for using in using_backends:
            try:
                index = self.connections[using].get_unified_index().get_index(sender)
                model_name = instance.__class__.__name__
                if model_name == 'Event':
                    is_not_published = instance.state not in State.get_published_states()
                    if is_not_published:
                        index.remove_object(instance, using=using)
                    else:
                        index.update_object(instance, using=using)
                else:
                    index.update_object(instance, using=using)
            except NotHandled as e:
                log.error(
                    'Failed to update %s object in search index for instance %s: %s' %
                    (instance.__class__.__name__, instance, e))
                pass

    def handle_delete(self, sender, instance, **kwargs):
        """
        Given an individual model instance, determine which backends the
        delete should be sent to & delete the object on those backends.

        Updated for this app to actually log an error on NotHandled (by
        default, BaseSignalProcessor just passes).

        Args:
          sender   (obj): The model class to receive signals from.
          instance (obj): The model instance.
          **kwargs: Arbitrary keyword arguments.
        """
        using_backends = self.connection_router.for_write(instance=instance)
        for using in using_backends:
            try:
                index = self.connections[using].get_unified_index().get_index(sender)
                index.remove_object(instance, using=using)
            except NotHandled as e:
                log.error(
                    'Failed to remove %s object from search index for instance %s: %s.' %
                    (instance.__class__.__name__, instance, e))
                pass
