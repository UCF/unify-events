from django.core.management.base import BaseCommand
from django.core.management      import call_command
from events.models               import Calendar, Event, EventInstance
from django.contrib.auth.models  import User
from django.contrib.webdesign    import lorem_ipsum
from datetime                    import datetime
from random                      import randint

lorem_ipsum.words_cust = lambda: lorem_ipsum.words(randint(3, 10), False).title()

class Command(BaseCommand):
	def handle(self, *args, **options):
		call_command('reset', 'events', 'auth', interactive=False)
		
		print 'Creating test users...',
		# Create users
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
			title=lorem_ipsum.words_cust(),
			description=lorem_ipsum.paragraph(),
			state=Event.Status.posted
		).instances.create(
			start=datetime(2011, 1, 1, 5, 0),
			end=datetime(2011, 1, 1, 6, 0),
			interval=EventInstance.Recurs.weekly,
			limit=52
		)
		obama_cal.events.create(
			title=lorem_ipsum.words_cust(),
			description=lorem_ipsum.paragraph(),
			state=Event.Status.posted
		).instances.create(
			start=datetime(2011, 1, 2, 4, 0),
			end=datetime(2011, 1, 2, 5, 30),
			interval=EventInstance.Recurs.weekly,
			limit=52
		)
		obama_cal.events.create(
			title=lorem_ipsum.words_cust(),
			description=lorem_ipsum.paragraph(),
			state=Event.Status.posted
		).instances.create(
			start=datetime(2011, 1, 2, 6, 0),
			end=datetime(2011, 1, 2, 7, 0),
			interval=EventInstance.Recurs.weekly,
			limit=52
		)
		obama_cal.events.create(
			title=lorem_ipsum.words_cust(),
			description=lorem_ipsum.paragraph(),
			state=Event.Status.posted
		).instances.create(
			start=datetime(2011, 1, 3, 5, 0),
			end=datetime(2011, 1, 3, 6, 0),
			interval=EventInstance.Recurs.weekly,
			limit=52
		)
		obama_cal.events.create(
			title=lorem_ipsum.words_cust(),
			description=lorem_ipsum.paragraph(),
			state=Event.Status.posted
		).instances.create(
			start=datetime(2011, 1, 4, 4, 25),
			end=datetime(2011, 1, 4, 5, 0),
			interval=EventInstance.Recurs.weekly,
			limit=52
		)
		obama_cal.events.create(
			title=lorem_ipsum.words_cust(),
			description=lorem_ipsum.paragraph(),
			state=Event.Status.posted
		).instances.create(
			start=datetime(2011, 1, 4, 6, 0),
			end=datetime(2011, 1, 4, 7, 0),
			interval=EventInstance.Recurs.weekly,
			limit=52
		)
		obama_cal.events.create(
			title=lorem_ipsum.words_cust(),
			description=lorem_ipsum.paragraph(),
			state=Event.Status.posted
		).instances.create(
			start=datetime(2011, 1, 5, 12, 0),
			end=datetime(2011, 1, 5, 12, 30),
			interval=EventInstance.Recurs.weekly,
			limit=52
		)
		
		romney_cal.events.create(
			title=lorem_ipsum.words_cust(),
			description=lorem_ipsum.paragraph(),
			state=Event.Status.posted
		).instances.create(
			start=datetime(2011, 1, 1, 5, 0),
			end=datetime(2011, 1, 1, 6, 0),
			interval=EventInstance.Recurs.daily,
			limit=52
		)
		romney_cal.events.create(
			title=lorem_ipsum.words_cust(),
			description=lorem_ipsum.paragraph(),
			state=Event.Status.posted
		).instances.create(
			start=datetime(2011, 1, 2, 5, 0),
			end=datetime(2011, 1, 2, 6, 0),
			interval=EventInstance.Recurs.daily,
			limit=52
		)
		romney_cal.events.create(
			title=lorem_ipsum.words_cust(),
			description=lorem_ipsum.paragraph(),
			state=Event.Status.posted
		).instances.create(
			start=datetime(2011, 1, 3, 5, 0),
			end=datetime(2011, 1, 3, 6, 0),
			interval=EventInstance.Recurs.daily,
			limit=52
		)
		romney_cal.events.create(
			title=lorem_ipsum.words_cust(),
			description=lorem_ipsum.paragraph(),
			state=Event.Status.posted
		).instances.create(
			start=datetime(2011, 1, 4, 5, 0),
			end=datetime(2011, 1, 4, 6, 0),
			interval=EventInstance.Recurs.daily,
			limit=52
		)
		romney_cal.events.create(
			title=lorem_ipsum.words_cust(),
			description=lorem_ipsum.paragraph(),
			state=Event.Status.posted
		).instances.create(
			start=datetime(2011, 1, 5, 5, 0),
			end=datetime(2011, 1, 5, 6, 0),
			interval=EventInstance.Recurs.daily,
			limit=52
		)
		print 'done'