"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from models import *
from fields import *

class SimpleTest(TestCase):
	fixtures = ['events.json',]
	
	def test_import_and_updates(self):
		calendar_one = Calendar.objects.all()[0]
		calendar_two = Calendar.objects.all()[1]
		
		orig = calendar_one.events.all()[0]
		copy = calendar_two.import_event(orig)
		self.assertEqual(copy.calendar, calendar_two)
		self.assertEqual(copy.title, orig.title)
		self.assertEqual(copy.instances.count(), orig.instances.count())
		
		orig.title = 'Robots Attack at Midnight'
		orig.save()
		copy = copy.pull_updates()
		self.assertEqual(copy.title, orig.title)
	
	def test_settings_field(self):
		events  = Event.objects.all()
		event   = events[0]
		test_id = event.pk
		self.assertEqual(type(event.settings), dict)
		event.settings['test_value'] = True
		event.save()
		
		event = Event.objects.get(pk=test_id)
		self.assertEqual(event.settings['test_value'], True)
	
	def test_coordinates(self):
		loc_1 = Location.objects.create(name="UCF", coordinates=(28.602006,-81.20038))
		self.assertEqual(type(loc_1.coordinates[0]), float)
		loc_2 = Location.objects.create(name="UCF", coordinates="28.602006,-81.20038")
		self.assertEqual(loc_1.coordinates[0], loc_2.coordinates[0])
	
	def test_unique_slug(self):
		calendar_orig = Calendar.objects.all()[0]
		calendar_copy = Calendar.objects.create(name=calendar_orig.name)
		self.assertNotEqual(calendar_orig.slug, calendar_copy.slug)
	
	def test_event_recurrence(self):
		from datetime import datetime
		calendar = Calendar.objects.all()[0]
		event    = calendar.events.create(title="Some Event", state=Event.Status.posted)
		event.instances.create(
			start=datetime(2011, 1, 1),
			end=datetime(2011, 1, 1, 2, 0, 0),
			interval=EventInstance.Recurs.daily,
			limit=3
		)
		event.instances.create(
			start=datetime(2011, 2, 1),
			end=datetime(2011, 2, 1, 2, 0, 0),
			interval=EventInstance.Recurs.weekly,
			limit=4
		)
		self.assertEqual(event.instances.count(), 7)
	
	def test_calendar_subscriptions(self):
		calendar_one = Calendar.objects.all()[0]
		calendar_two = Calendar.objects.all()[1]
		one_cnt = calendar_one.event_instances.count()
		two_cnt = calendar_two.event_instances.count()
		self.assertEqual(calendar_one.events_and_subs.count(), one_cnt + two_cnt)
