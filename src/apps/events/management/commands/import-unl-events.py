from django.core.management.base import BaseCommand
from unlevents.models            import UNLCalendar, UNLEvent, UNLEventdatetime, \
									UNLLocation, UNLUserHasPermission,UNLCalendarHasEvent, \
									UNLEventHasEventtype, UNLEventtype, UNLUserHasPermission
from django.contrib.auth.models  import User
from util                        import LDAPHelper
from django.conf                 import settings
from events.models               import Calendar,Event,EventInstance,Location,Category
import logging

# Connect to LDAP and bind for searching later
ldap = LDAPHelper()
LDAPHelper.bind(ldap.connection,settings.LDAP_NET_SEARCH_USER,settings.LDAP_NET_SEARCH_PASS)

MISSING_USERNAMES = []

class Command(BaseCommand):
	def handle(self, *args, **options):

		self.create_categories()

		old_calendars = UNLCalendar.objects.all()
		for old_calendar in old_calendars:

			# Check if the old calendar creator exists in our DB
			calendar_creator = self.get_create_user(str(old_calendar.uidcreated))
			if calendar_creator is not None:
				new_calendar = Calendar(name=old_calendar.name,creator=calendar_creator)
				try:
					new_calendar.save()
				except Exception, e:
					logging.error('Unable to save calendar `%s`: %s' % (old_calendar.name, str(e)))
				else:

					# Editors
					# Assume if they had any permissions at all, they are an editor
					for uid in UNLUserHasPermission.objects.filter(calendar_id=old_calendar.id).values_list('user_uid').distinct():
						uid = uid[0]
						editor = self.get_create_user(str(uid))
						if editor is not None:
							new_calendar.editors.add(editor)

					# Events
					for old_calendar_event in UNLCalendarHasEvent.objects.filter(calendar_id = old_calendar.id):
						try:
							old_event = UNLEvent.objects.get(id=old_calendar_event.event_id)
						except UNLEvent.DoesNotExist:
							logging.error('Has event missing %d' % old_calendar_event.event_id)

						old_title = old_event.title
						if len(old_title) > 128:
							old_title = old_title[0:127]
						elif old_event.subtitle is not None and len(old_event.title + ' - ' + old_event.subtitle) < 128:
							old_title += ' - ' + old_event.subtitle

						new_event = Event(title=old_title,description=old_event.description,calendar=new_calendar)
						
						# TODO - images

						# Statuses: pending, posted, archived
						state = None
						if old_calendar_event.status == 'pending':
							new_event.state = Event.Status.pending
						elif old_calendar_event.status == 'posted' or old_calendar_event.status == 'archived':
							new_event.state = Event.Status.posted
						else:
							logging.error('Unknown old event status `%s`' % old_calendar_event.status)
							continue
						
						event_creator = self.get_create_user(str(old_event.uidcreated))
						if event_creator is not None:
							new_event.creator = event_creator
						
							try:
								new_event.save()
							except Exception, e:
								logging.error('Unable to save new event `%s`: %s' % (new_event.title,str(e)))
								continue
							else:
								# Event Type -> Category
								category = self.get_event_category(old_event)
								if category is not None:
									new_event.categories.add(category)
								
								# Instances
								for old_instance in UNLEventdatetime.objects.filter(event_id=old_event.id):
									new_instance       = EventInstance(event=new_event)
									new_instance.start = old_instance.starttime
									new_instance.end   = old_instance.endtime

									# TODO - Location
									
									try:
										new_instance.save()
									except Exception, e:
										logging.error('Unable to save event instance for event `%s`: %s' % (new_event.title,str(e)))

	def get_event_category(self,old_event):
		try:
			event_event_type = UNLEventHasEventtype.objects.get(event_id=old_event.id)
		except UNLEventHasEventtype.DoesNotExist:
			pass
		else:
			try:
				event_type = UNLEventtype.objects.get(id=event_event_type.eventtype_id)
			except UNLEventtype.DoesNotExist:
				pass
			else:
				try:
					category = Category.objects.get(name=event_type.name)
				except Category.DoesNotExist:
					logging.error('Category for event_type_id `%d` does not exist.' % event_event_type.eventtype_id)
				else:
					return category

	def create_categories(self):
		for event_type in UNLEventtype.objects.all():
			created, category = Category.objects.get_or_create(name=event_type.name)

	def get_create_user(self,username):

		if username in MISSING_USERNAMES: return None
		
		try:
			user = User.objects.get(username=username)
			logging.info('User %s found in new system.' % username)
			return user
		except User.DoesNotExist:
			logging.info('User %s does not exist in new system. Looking up in the NET domain.' % username)
			try:
				ldap_user = LDAPHelper.search_single(ldap.connection,username)
			except LDAPHelper.NoUsersFound:
				MISSING_USERNAMES.append(username)
			except Exception, e:
				logging.error(str(e) + ' ' + username)
			else:
				try:
					guid = LDAPHelper.extract_guid(ldap_user)						
				except LDAPHelper.MissingAttribute:
					logging.error('User %s does not have a GUID in the NET domain' % username)
				else:
					user = User(username=username)
					# Try to extract some other details

					try:
						user.first_name = LDAPHelper.extract_firstname(ldap_user)
					except LDAPHelper.MissingAttribute:
						pass
					try:
						user.last_name = LDAPHelper.extract_lastname(ldap_user)
					except LDAPHelper.MissingAttribute:
						pass
					try:
						user.email = LDAPHelper.extract_email(ldap_user)
					except LDAPHelper.MissingAttribute:
						pass
					
					try:
						user.save()
						user.profile.guid = guid
						user.profile.save()
					except Exception, e:
						logging.error('Unable to save user `%s`: %s' % (username,str(e)))
					else:
						return user