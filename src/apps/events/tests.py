"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from models import *

class SimpleTest(TestCase):
	def setUp(self):
		self.users = (
			User.objects.create(username="user_1"),
			User.objects.create(username="user_2"),
			User.objects.create(username="user_3"),
		)
		self.calendars = (
			Calendar.objects.create(name="calendar_1", creator=self.users[0]),
			Calendar.objects.create(name="calendar_2", creator=self.users[1]),
			Calendar.objects.create(name="calendar_3", creator=self.users[2]),
		)
		
	
	def test_unique_slug(self):
		c0 = self.calendars[0]
		c1 = Calendar.objects.create(name="calendar_1", creator=self.users[0])
		self.assertNotEqual(c0.slug, c1.slug)
	
	def test_event_lookup(self):
		from datetime import datetime, timedelta
		
		e1 = self.calendars[0].create_event(
			title='Health Care Reform',
			description='HA ' * 40,
			state=Event.Status.pending
		)
		e2 = self.calendars[1].create_event(
			title='Fiscal Responsibility',
			description='@_@',
			state=Event.Status.pending
		)
		start = datetime.now()
		end   = datetime.now() + timedelta(hours=1)
		e1.instances.create(
			start=start,
			end=end,
			interval=EventInstance.Recurs.weekly,
			limit=1
		)
		e2.instances.create(
			start=start,
			end=end,
			interval=EventInstance.Recurs.daily,
			limit=13
		)
		
		end = start + timedelta(days=7)
		 
		self.assertEqual(
			len(self.calendars[0].find_event_instances(start=start, end=end)),
			2
		)
	
	def test_event_recurrence(self):
		from datetime import datetime, timedelta
		
		e = self.calendars[0].create_event(
			title='Glenn Beck Rally',
			description='''Glenn Beck speaks some jibberish, Palin uses the 
			words God, country, soldiers, armed forces, christian, freedom,
			constitution, and hockey so much that semantic satiation kicks in.
			''',
			state=Event.Status.pending
		)
		limit = 70
		start = datetime.now()
		end   = start + timedelta(hours=1)
		lend  = end + timedelta(days=limit)
		e.instances.create(
			start=start,
			end=end,
			interval=EventInstance.Recurs.daily,
			limit=limit
		)
		self.assertEqual(e.instances.all().order_by('-end')[0].end, lend)
		self.assertEqual(e.instances.count(), limit + 1)
	
	def test_calendar_subscriptions(self):
		from datetime import datetime
		c1 = Calendar.objects.create(name='Robot')
		c2 = Calendar.objects.create(name='Moobot')
		self.assertEqual(len(c1.events_and_subs), 0)
		e1 = c1.create_event(title='Robot Attack', state=Event.Status.pending)
		e2 = c2.create_event(title='Cow Attack', state=Event.Status.pending)
		e1.instances.create(start=datetime.now(), end=datetime.now())
		e2.instances.create(start=datetime.now(), end=datetime.now())
		c1.subscriptions.add(c2)
		self.assertEqual(len(c1.events_and_subs), 2)
		e3 = c2.create_event(title='Another Cow Attack', state=Event.Status.pending)
		e3.instances.create(start=datetime.now(), end=datetime.now())
		self.assertEqual(len(c1.events_and_subs), 3)
		self.assertEqual(len(c2.events_and_subs), 2)
