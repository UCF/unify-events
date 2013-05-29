from django.core.management.base import BaseCommand
from django.core.management      import call_command
from events.models               import Calendar, Event, EventInstance, Tag, Location
from django.contrib.auth.models  import User
from django.contrib.webdesign    import lorem_ipsum
from datetime                    import datetime, timedelta
from random                      import randint, choice

lorem_ipsum.words_cust = lambda: lorem_ipsum.words(randint(3, 10), False).title()

class Command(BaseCommand):
	def handle(self, *args, **options):
		call_command('reset', 'events', 'auth', interactive=False)
		
		print 'Creating test users...',
		# Create users
		test_user = User.objects.create(username="test", password="test", first_name="Patrick", last_name="Burt")
		print 'done'
		
		print 'Creating calendars for test users...',
		# Create calendars
		cal = test_user.owned_calendars.create(name="Test Calendar")
		print 'done'
		
		print 'Creating events for new calendars...',
		tag_choices = map(
			lambda t: Tag.objects.create(name=t),
			set(lorem_ipsum.words(20, False).lower().split())
		)
		contact_name_choices  = (None, 'Spork Belvadere', 'Captain ImABadGuy', 'Bill Paxton', 'Admiral Evildude')
		contact_phone_choices = (None, '407-123-3215', '563-456-4123', '123-456-4448')
		contact_email_choices = (None, 'john@doe.com', 'anon@ymous.com', 'event@contact.com')
		location_choices = (
			Location.objects.create(name="Student Union"),
			Location.objects.create(name="Library"),
			Location.objects.create(name="Arena"),
			Location.objects.create(name="Visual Arts Building"),
			Location.objects.create(name="Patrick's House"),
		)
		for i in range(1, 8):
			hour    = randint(8, 20)
			minutes = choice([15, 30, 45, 0, 0, 0])
			start   = datetime(datetime.now().year, 1, i, hour, minutes)
			end     = start + timedelta(hours=choice([1, 2, 3, 24, 25, 26, 48, 49, 50]))
			
			tags = list()
			for j in range(0, randint(1, 5)):
				tags.append(choice(tag_choices))
			
			event = cal.events.create(
				title=lorem_ipsum.words_cust(),
				description=lorem_ipsum.paragraph(),
				state=Event.Status.posted,
				owner=test_user,
				contact_name=choice(contact_name_choices),
				contact_phone=choice(contact_phone_choices),
				contact_email=choice(contact_email_choices)
			)
			event.tags.add(*tags)
			
			instance = event.instances.create(
				location=choice(location_choices),
				start=start,
				end=end,
				interval=EventInstance.Recurs.weekly,
				until=datetime(datetime.now().year + 1, 1, 1)
			)
		print 'done'