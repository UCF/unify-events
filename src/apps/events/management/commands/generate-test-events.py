from django.core.management.base import BaseCommand
from django.core.management      import call_command
from events.models               import Calendar, Event, EventInstance
from django.contrib.auth.models  import User
from datetime                    import datetime

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
			title="Curing Old Age",
			description="So I created a \"panel\" for the care of the elderly...",
			state=Event.Status.posted
		).instances.create(
			start=datetime(2011, 1, 1, 5, 0),
			end=datetime(2011, 1, 1, 6, 0),
			interval=EventInstance.Recurs.weekly,
			limit=52
		)
		obama_cal.events.create(
			title="Winning a Nobel Peace Prize",
			description="What do change, hope, and cruise missiles all have in common?  This guy!",
			state=Event.Status.posted
		).instances.create(
			start=datetime(2011, 1, 2, 4, 0),
			end=datetime(2011, 1, 2, 5, 30),
			interval=EventInstance.Recurs.weekly,
			limit=52
		)
		obama_cal.events.create(
			title="How to Escalate a Current War",
			description="The key is in the rhetoric.",
			state=Event.Status.posted
		).instances.create(
			start=datetime(2011, 1, 3, 5, 0),
			end=datetime(2011, 1, 3, 6, 0),
			interval=EventInstance.Recurs.weekly,
			limit=52
		)
		obama_cal.events.create(
			title="How to Begin Another War",
			description="War Powers what?",
			state=Event.Status.posted
		).instances.create(
			start=datetime(2011, 1, 4, 4, 25),
			end=datetime(2011, 1, 4, 5, 0),
			interval=EventInstance.Recurs.weekly,
			limit=52
		)
		obama_cal.events.create(
			title="Closing Gitmo, Pros and Cons",
			description="No comment.",
			state=Event.Status.posted
		).instances.create(
			start=datetime(2011, 1, 5, 12, 0),
			end=datetime(2011, 1, 5, 12, 30),
			interval=EventInstance.Recurs.weekly,
			limit=52
		)
		
		romney_cal.events.create(
			title="Of Course Corporations are Llamas",
			description="Corporations are comprised of people.  People eat food.  Llamas eat food.  Therefore...",
			state=Event.Status.posted
		).instances.create(
			start=datetime(2011, 1, 1, 5, 0),
			end=datetime(2011, 1, 1, 6, 0),
			interval=EventInstance.Recurs.daily,
			limit=52
		)
		romney_cal.events.create(
			title="I Love Healthcare Reform",
			description="It's so nice to be here in Massachusetts.",
			state=Event.Status.posted
		).instances.create(
			start=datetime(2011, 1, 2, 5, 0),
			end=datetime(2011, 1, 2, 6, 0),
			interval=EventInstance.Recurs.daily,
			limit=52
		)
		romney_cal.events.create(
			title="I Hate Healthcare Reform",
			description="It's so nice to be here in Iowa.",
			state=Event.Status.posted
		).instances.create(
			start=datetime(2011, 1, 3, 5, 0),
			end=datetime(2011, 1, 3, 6, 0),
			interval=EventInstance.Recurs.daily,
			limit=52
		)
		romney_cal.events.create(
			title="The Solution is Lower Taxes",
			description="The rich are job creators people, you can't tax them!  They'll never create jobs!",
			state=Event.Status.posted
		).instances.create(
			start=datetime(2011, 1, 4, 5, 0),
			end=datetime(2011, 1, 4, 6, 0),
			interval=EventInstance.Recurs.daily,
			limit=52
		)
		romney_cal.events.create(
			title="The Solution is Always Lower Taxes",
			description="The balanced approach is lower taxes!  Yay, no taxes for everybody.  Make it rain!",
			state=Event.Status.posted
		).instances.create(
			start=datetime(2011, 1, 5, 5, 0),
			end=datetime(2011, 1, 5, 6, 0),
			interval=EventInstance.Recurs.daily,
			limit=52
		)
		print 'done'