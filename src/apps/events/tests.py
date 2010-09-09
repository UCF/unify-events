"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from models import *

class SimpleTest(TestCase):
	def test_unique_slug(self):
		c1 = Calendar.objects.create(name="Spork's House")
		c2 = Calendar.objects.create(name="Spork's House")
		c3 = Calendar.objects.create(name="Spork2Home")
		c4 = Calendar.objects.create(name="Spork2Home")
		self.assertNotEqual(c1.slug, c2.slug)
		self.assertNotEqual(c3.slug, c4.slug)
	
	def test_event_recurrence(self):
		from datetime import datetime
		
		e = Event.objects.create(
			title='Glenn Beck Rally',
			description='''Glenn Beck speaks some jibberish, Palin uses the 
			words God, country, soldiers, armed forces, christian, freedom,
			constitution, and hockey so much that semantic satiation kicks in.
			'''
		)
		e.instances.create(
			start=datetime.now(),
			end=datetime.now(),
			interval=EventInstance.Recurs.daily,
			limit=70
		)
		self.assertEqual(e.instances.count(), 71)
	
	def test_calendar_subscriptions(self):
		c1 = Calendar.objects.create(name='Robot')
		c2 = Calendar.objects.create(name='Moobot')
		self.assertEqual(len(c1.events_and_subs), 0)
		c1.create_event(title='Robot Attack')
		c2.create_event(title='Cow Attack')
		c1.subscriptions.add(c2)
		self.assertEqual(len(c1.events_and_subs), 2)
		c2.create_event(title='Another Cow Attack')
		self.assertEqual(len(c1.events_and_subs), 3)
