from django.core.management.base import BaseCommand
from django.core.management      import call_command
from events.models               import Calendar, Event, EventInstance
from django.contrib.auth.models  import User
from django.contrib.webdesign    import lorem_ipsum
from datetime                    import datetime
from random                      import randint, choice

lorem_ipsum.words_cust = lambda: lorem_ipsum.words(randint(3, 10), False).title()

class Command(BaseCommand):
	def handle(self, *args, **options):
		call_command('reset', 'events', 'auth', interactive=False)
		
		print 'Creating test users...',
		# Create users
		test_user = User.objects.create(username="test", password="test")
		print 'done'
		
		print 'Creating calendars for test users...',
		# Create calendars
		cal = test_user.owned_calendars.create(name="Test Calendar")
		print 'done'
		
		print 'Creating events for new calendars...',
		for i in range(1, 7):
			hour_start = randint(8,20)
			hour_end   = hour_start + randint(1,3)
			minutes    = choice([15, 30, 45, 0, 0, 0])
			cal.events.create(
				title=lorem_ipsum.words_cust(),
				description=lorem_ipsum.paragraph(),
				state=Event.Status.posted
			).instances.create(
				start=datetime(datetime.now().year, 1, i, hour_start, minutes),
				end=datetime(datetime.now().year, 1, i, hour_end, minutes),
				interval=EventInstance.Recurs.weekly,
				limit=52
			)
		print 'done'