import settings
from datetime import datetime, date
from django.core.management.base import BaseCommand, CommandError

from seo.models import InternalLink, InternalLinkRecord
from seo import util
from events.models import Event

from queue import Queue
from threading import Thread, Lock

from tqdm import tqdm

class Command(BaseCommand):
    help = 'Adds internal links into event descriptions'

    def add_arguments(self, parser) -> None:
        """
        Adds arguments to the parser
        """
        parser.add_argument(
            '--process-current-events',
            dest='process_current_events',
            action='store_true',
            default=False
        )

        parser.add_argument(
            '--force',
            dest='force',
            action='store_true',
            default=False
        )

        parser.add_argument(
            '--reprocess-before',
            dest='events_before',
            type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
            default=None
        )

        parser.add_argument(
            '--reprocess-after',
            dest='events_after',
            type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
            default=None
        )

        parser.add_argument(
            '--max-threads',
            dest='max_threads',
            type=int,
            default=10
        )


    def handle(self, *args, **options):
        """
        Entry point for the command
        """
        self.process_current_events = options.get('process_current_events', False)
        self.force_reprocess = options.get('force', False)
        self.events_before = options.get('events_before', None)
        self.events_after = options.get('events_after', None)
        self.max_threads = options.get('max_threads', 10)
        self.process_date_time = datetime.now()

        # Everything we need for multithreading fun!
        self.events_queue = Queue()
        self.events_queue_lock = Lock()
        self.progress_lock = Lock()
        self.database_lock = Lock()

        # Set the self.events object to the events
        # we will be processing
        self.__get_events()

        self.progress = tqdm(total=self.events.count())

        # Fill up the self.events_queue for
        # multithreaded processing
        self.__prepare_events()

        # Spin up the processing threads and let them
        # run until the queue is empty
        self.__async_process_events()

        self.__report_stats()

    def __get_events(self):
        """
        Gets the events to be processed
        """
        retval = Event.objects.all()

        # If we're not forcing reprocessing,
        # filter to only events that have not been
        # checked.
        if not self.force_reprocess:
            retval = retval.filter(
                internal_link_checked__isnull=True
            )


        if not self.process_current_events:
            retval = retval.filter(
                event_instances__start__lt=self.process_date_time,
                event_instances__end__lt=self.process_date_time
            )

        if self.events_before:
            retval = retval.filter(
                event_instances__start__lt=self.events_before,
                event_instances__end__lt=self.events_before
            )

        if self.events_after:
            retval = retval.filter(
                event_instances__start__gte=self.events_after,
                event_instances__end__gte=self.events_after
            )

        self.events = retval.distinct()

    def __prepare_events(self):
        """
        Adds the events to the queue
        """
        for event in self.events.all():
            self.events_queue.put(event)


    def __process_events(self):
        """
        The function that actually processes the events
        """
        while True:
            try:
                event = None
                with self.events_queue_lock:
                    event = self.events_queue.get()

                try:
                    with self.database_lock:
                        desc = util.internal_links(event, self.process_date_time)
                    event.description = desc
                    event.internal_link_checked = self.process_date_time
                    with self.database_lock:
                        event.save()

                except Exception as e:
                    self.stderr.write(
                        self.style.ERROR(f"Error saving to database: {e}")
                    )
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(f"There was an exception: {e}")
                )
            finally:
                with self.progress_lock:
                    self.progress.update(1)
                self.events_queue.task_done()


    def __async_process_events(self):
        """
        Starts up the processing threads and runs
        them until the events_queue is empty
        """
        for _ in range(self.max_threads):
            thread = Thread(
                target=self.__process_events,
                daemon=True
            )
            thread.start()

        self.events_queue.join()


    def __report_stats(self):
        replacements_made = InternalLinkRecord.objects.filter(
            updated_at__gte=self.process_date_time
        ).count()

        self.stdout.writelines([
            self.style.SUCCESS("All finished processing"),
            self.style.NOTICE(f"Records updated: {replacements_made}")
        ])
