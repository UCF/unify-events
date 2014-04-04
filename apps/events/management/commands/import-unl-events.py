import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from unlevents.models import UNLCalendar
from unlevents.models import UNLEvent
from unlevents.models import UNLEventdatetime
from unlevents.models import UNLLocation
from unlevents.models import UNLUserHasPermission
from unlevents.models import UNLCalendarHasEvent
from unlevents.models import UNLEventHasEventtype
from unlevents.models import UNLEventtype
from unlevents.models import UNLSubscription
from unlevents.models import UNLUserHasPermission
from util import LDAPHelper
from events.models import Calendar
from events.models import Category
from events.models import Event
from events.models import EventInstance
from events.models import Location
from events.models import State


# Connect to LDAP and bind for searching later
ldap = LDAPHelper()
LDAPHelper.bind(ldap.connection,settings.LDAP_NET_SEARCH_USER,settings.LDAP_NET_SEARCH_PASS)

MISSING_USERNAMES = []


class Command(BaseCommand):
    def handle(self, *args, **options):

        self.create_categories()
        self.create_locations()

        old_calendars = UNLCalendar.objects.all()
        for old_calendar in old_calendars:

            # Check if the old calendar creator exists in our DB
            calendar_creator = self.get_create_user(str(old_calendar.uidcreated))
            if calendar_creator is not None:
                new_calendar = Calendar(title=old_calendar.name, owner=calendar_creator)
                new_calendar.pk = old_calendar.id
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
                        if len(old_title) > 255:
                            old_title = old_title[0:254]
                        elif old_event.subtitle is not None and len(old_event.title + ' - ' + old_event.subtitle) < 255:
                            old_title += ' - ' + old_event.subtitle

                        old_contact_name = old_event.listingcontactname
                        if not old_contact_name:
                            old_contact_name = calendar_creator.first_name

                        # check to see if the contact name is too long
                        if len(old_contact_name) > 64:
                            old_contact_name = old_contact_name[0:63]

                        old_contact_email = old_event.listingcontactemail
                        if not old_contact_email:
                            if calendar_creator.email:
                                old_contact_email = calendar_creator.email
                            else:
                                old_contact_email = 'webcom@ucf.edu'

                        old_contact_phone = old_event.listingcontactphone

                        new_event = Event(title=old_title,
                                          description=old_event.description,
                                          calendar=new_calendar,
                                          contact_name=old_contact_name,
                                          contact_email=old_contact_email,
                                          contact_phone=old_contact_phone)

                        # Statuses: pending, posted, archived
                        state = None
                        if old_calendar_event.status == 'pending':
                            new_event.state = State.pending
                        elif old_calendar_event.status == 'posted' or old_calendar_event.status == 'archived':
                            new_event.state = State.posted
                        else:
                            logging.error('Unknown old event status `%s`' % old_calendar_event.status)
                            continue

                        event_creator = self.get_create_user(str(old_event.uidcreated))
                        if event_creator is not None:
                            new_event.owner = event_creator

                            # Event Type -> Category
                            category = self.get_event_category(old_event)
                            if category is not None:
                                new_event.category = category

                            try:
                                new_event.save()
                            except Exception, e:
                                logging.error('Unable to save new event `%s`: %s' % (new_event.title,str(e)))
                                continue
                            else:
                                # Instances
                                for old_instance in UNLEventdatetime.objects.filter(event_id=old_event.id):
                                    new_instance       = EventInstance(event=new_event)
                                    new_instance.start = old_instance.starttime
                                    new_instance.end   = old_instance.endtime

                                    old_location_id = old_instance.location_id
                                    if not old_location_id:
                                        old_location_id = 1

                                    # Location
                                    try:
                                        old_location = UNLLocation.objects.get(id=old_location_id)
                                    except UNLLocation.DoesNotExist:
                                        logging.info('UNL event instance location not in UNL Location table: %d' % old_location_id)
                                    else:
                                        if old_location.name:
                                            # check to see if the location name is too long
                                            old_locatin_name = old_location.name
                                            if len(old_locatin_name) > 256:
                                                old_locatin_name = old_locatin_name[0:256]

                                            try:
                                                new_instance.location = Location.objects.get(title__iexact=old_locatin_name)
                                            except Location.DoesNotExist:
                                                logging.error('No Location for UNL Location %s' % old_locatin_name)

                                    try:
                                        new_instance.save()
                                    except Exception, e:
                                        logging.error('Unable to save event instance for event `%s`: %s' % (new_event.title,str(e)))

        subscriptions = UNLSubscription.objects.all()
        for sub in subscriptions:
            if sub.searchcriteria is not None:
                subscription_id = sub.searchcriteria.split()[0].replace('calendar_has_event.calendar_id=', '')
                try:
                    unl_subscription_cal = UNLCalendar.objects.get(id=subscription_id)
                except UNLCalendar.DoesNotExist:
                    logging.error('UNL subscription calendar does not exist ID: %s' , subscription_id)
                else:
                    try:
                        subscription_cal = Calendar.objects.get(title=unl_subscription_cal.name)
                    except Calendar.DoesNotExist:
                        logging.error('Subscription calendar does not exist name: %s with UNL ID %s' % (unl_subscription_cal.name, subscription_id))
                    else:
                        try:
                            unl_calendar = UNLCalendar.objects.get(id=sub.calendar_id)
                        except UNLCalendar.DoesNotExist:
                            logging.error('UNL calendar does not exist ID: %s' , sub.calendar_id)
                        else:
                            try:
                                calendar = Calendar.objects.get(title=unl_calendar.name)
                            except Calendar.DoesNotExist:
                                logging.error('Calendar does not exist %s with UNL ID %s' % (unl_calendar.name, sub.calendar_id))
                            else:
                                calendar.subscriptions.add(subscription_cal)
                                calendar.save()


    def get_event_category(self,old_event):
        try:
            event_event_type = UNLEventHasEventtype.objects.get(event_id=old_event.id)
        except UNLEventHasEventtype.DoesNotExist:
            category = Category.objects.get(title='Other')
        else:
            try:
                event_type = UNLEventtype.objects.get(id=event_event_type.eventtype_id)
            except UNLEventtype.DoesNotExist:
                category = Category.objects.get(title='Other')
            else:
                try:
                    category = Category.objects.get(title=event_type.name)
                except Category.DoesNotExist:
                    category = Category.objects.get(title='Other')
                    logging.error('Category for event_type_id `%d` does not exist. Using Other Cateogry' % event_event_type.eventtype_id)
        return category

    def create_categories(self):
        for event_type in UNLEventtype.objects.all():
            category, created = Category.objects.get_or_create(title=event_type.name)

    def create_locations(self):
        LOCATION_NAMES = []
        for name,mapurl,room in UNLLocation.objects.values_list('name','mapurl','room'):

            if name:
                # check to see if the location name is too long
                if len(name) > 256:
                    name = name[0:256]

                if name.lower() not in LOCATION_NAMES:
                    LOCATION_NAMES.append(name.lower())
                    new_location = Location(title=name, url=mapurl, room=room)
                    try:
                        new_location.save()
                    except Exception, e:
                        logging.error('Unable to save location %s: %s' % (name, str(e)))

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
                logging.error('User %s does not exist in the NET domain.' % username)
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
                        logging.error('User %s does not have a email' % username)

                    try:
                        user.save()
                        user.profile.guid = guid
                        user.profile.save()
                    except Exception, e:
                        logging.error('Unable to save user `%s`: %s' % (username,str(e)))
                    else:
                        return user
