import logging

from django.db import models
from haystack import signals
from haystack.exceptions import NotHandled

log = logging.getLogger(__name__)


class CustomHaystackSignalProcessor(signals.BaseSignalProcessor):
    """
    A convenient way to attach Haystack to Django's signals & cause things to
    index.

    Signals that trigger handle_save and handle_delete are defined where the
    respective model is defined (e.g. events/models/event.py).  Only models
    that get indexed by Haystack should trigger the signal processor.
    """

    def handle_save(self, sender, instance, **kwargs):
        """
        Given an individual model instance, determine which backends the
        update should be sent to & update the object on those backends.

        Updated for thie app to degrade gracefully if the search backend
        bombs for whatever reason.

        Args:
          sender   (obj): The model class to receive signals from.
          instance (obj): The model instance.
          **kwargs: Arbitrary keyword arguments.
        """
        using_backends = self.connection_router.for_write(instance=instance)
        for using in using_backends:
            try:
                index = self.connections[using].get_unified_index().get_index(sender)
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

        Updated for this app to degrade gracefully if the search backend
        bombs for whatever reason.

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
