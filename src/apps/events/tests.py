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
		c2 = Calendar.objects.create(name="Spork")
		c3 = Calendar.objects.create(name="Spork's House")
		
		self.assertNotEqual(c1.slug, c3.slug)
