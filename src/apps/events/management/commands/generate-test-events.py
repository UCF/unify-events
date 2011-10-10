from django.core.management.base import BaseCommand
from django.core.management      import call_command
from events.models               import Calendar, Event, EventInstance
from django.contrib.auth.models  import User
from datetime                    import datetime
from threading                   import Thread

class Command(BaseCommand):
	def handle(self, *args, **options):
		call_command('flush', interactive=False)
		
		print 'Creating test users...',
		# Create users
		users = list()
		obama  = User.objects.create(username="obama", password="obama")
		romney = User.objects.create(username="romney", password="romney")
		print 'done'
		
		print 'Creating calendars for test users...',
		# Create calendars
		obama_cal  = obama.owned_calendars.create(name="Obama the Blue")
		romney_cal = romney.owned_calendars.create(name="Romney the Red")
		print 'done'
		
		print 'Creating events for new calendars...',
		# Create events
		obama_cal.events.create(
			title="Spreading the Wealth: A Marxist Tale",
			state=Event.Status.posted
		).instances.create(
			start=datetime(2011, 1, 1, 5, 0),
			end=datetime(2011, 1, 1, 6, 0),
			interval=EventInstance.Recurs.weekly,
			limit=52
		)
		obama_cal.events.create(
			title="How to Win a Nobel Peace Prize",
			state=Event.Status.posted
		).instances.create(
			start=datetime(2011, 1, 2, 4, 0),
			end=datetime(2011, 1, 2, 5, 30),
			interval=EventInstance.Recurs.weekly,
			limit=52
		)
		obama_cal.events.create(
			title="How to Escalate a Current war",
			state=Event.Status.posted
		).instances.create(
			start=datetime(2011, 1, 3, 5, 0),
			end=datetime(2011, 1, 3, 6, 0),
			interval=EventInstance.Recurs.weekly,
			limit=52
		)
		obama_cal.events.create(
			title="How to Begin Another War",
			state=Event.Status.posted
		).instances.create(
			start=datetime(2011, 1, 4, 4, 25),
			end=datetime(2011, 1, 4, 5, 0),
			interval=EventInstance.Recurs.weekly,
			limit=52
		)
		obama_cal.events.create(
			title="Closing Gitmo, Pros and Cons",
			state=Event.Status.posted
		).instances.create(
			start=datetime(2011, 1, 5, 12, 0),
			end=datetime(2011, 1, 5, 12, 30),
			interval=EventInstance.Recurs.weekly,
			limit=52
		)
		
		romney_cal.events.create(
			title="Of Course Corporations are Llamas",
			state=Event.Status.posted
		).instances.create(
			start=datetime(2011, 1, 1, 5, 0),
			end=datetime(2011, 1, 1, 6, 0),
			interval=EventInstance.Recurs.daily,
			limit=52
		)
		romney_cal.events.create(
			title="I Love Healthcare Reform",
			state=Event.Status.posted
		).instances.create(
			start=datetime(2011, 1, 2, 5, 0),
			end=datetime(2011, 1, 2, 6, 0),
			interval=EventInstance.Recurs.daily,
			limit=52
		)
		romney_cal.events.create(
			title="I Hate Healthcare Reform",
			state=Event.Status.posted
		).instances.create(
			start=datetime(2011, 1, 3, 5, 0),
			end=datetime(2011, 1, 3, 6, 0),
			interval=EventInstance.Recurs.daily,
			limit=52
		)
		romney_cal.events.create(
			title="The Solution is Lower Taxes",
			state=Event.Status.posted
		).instances.create(
			start=datetime(2011, 1, 4, 5, 0),
			end=datetime(2011, 1, 4, 6, 0),
			interval=EventInstance.Recurs.daily,
			limit=52
		)
		romney_cal.events.create(
			title="The Solution is Always Lower Taxes",
			state=Event.Status.posted
		).instances.create(
			start=datetime(2011, 1, 5, 5, 0),
			end=datetime(2011, 1, 5, 6, 0),
			interval=EventInstance.Recurs.daily,
			limit=52
		)
		print 'done'