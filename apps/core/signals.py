from haystack import signals
from haystack.exceptions import NotHandled


class CustomRealtimeSignalProcessor(signals.RealtimeSignalProcessor):
    def handle_save(self, sender, instance, **kwargs):
        """
        Given an individual model instance, determine which backends the
        update should be sent to & update the object on those backends.

        Updated for this app to degrade gracefully if the search backend
        bombs for whatever reason.
        """
        using_backends = self.connection_router.for_write(instance=instance)
        for using in using_backends:
            try:
                index = self.connections[using].get_unified_index().get_index(sender)
                try:
                	index.update_object(instance, using=using)
                except Exception, e:
                    # The search engine can't be accessed, or something went wrong.
                    # Continue anyway
                    pass
            except NotHandled, e:
                # TODO: Maybe log it or let the exception bubble?
                pass

    def handle_delete(self, sender, instance, **kwargs):
        """
        Given an individual model instance, determine which backends the
        delete should be sent to & delete the object on those backends.

        Updated for this app to degrade gracefully if the search backend
        bombs for whatever reason.
        """
        using_backends = self.connection_router.for_write(instance=instance)
        for using in using_backends:
            try:
                index = self.connections[using].get_unified_index().get_index(sender)
                try:
                    index.remove_object(instance, using=using)
                except Exception, e:
                    # The search engine can't be accessed, or something went wrong.
                    # Continue anyway
                    pass
            except NotHandled, e:
                # TODO: Maybe log it or let the exception bubble?
                pass