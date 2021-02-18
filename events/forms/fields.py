import logging

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from events.forms.widgets import InlineLDAPSearch
from util import LDAPHelper


class InlineLDAPSearchField(forms.ModelMultipleChoiceField):

    def __init__(self, *args, **kwargs):
        kwargs['widget'] = InlineLDAPSearch()
        super(InlineLDAPSearchField, self).__init__(*args, **kwargs)

    def clean(self, guids_usernames):
        """
            The users submitted by this field my not be users
            in our system yet. Check to see if they exist. If
            they don't, create them. Pass all the PKs to the
            super.
        """
        users = []
        if guids_usernames is not None and len(guids_usernames) > 0:
            try:
                ldap = LDAPHelper()
                LDAPHelper.bind(ldap.connection, settings.LDAP_NET_SEARCH_USER,settings.LDAP_NET_SEARCH_PASS)
            except Exception as e:
                logging.error(str(e))
                raise ValidationError('Unable to connect to LDAP')
            else:
                if isinstance(guids_usernames, str):
                    guids_usernames = (guids_usernames,)
                for guid, username in (tuple(gu.split('|')) for gu in guids_usernames):
                    try:
                        user = User.objects.get(profile__guid=guid)
                    except User.DoesNotExist:
                        try:
                            ldap_user = LDAPHelper.search_single(ldap.connection, username)
                        except Exception as e:
                            logging.error(str(e))
                            raise ValidationError('Looking up `%s` in LDAP failed.' % username)
                        else:
                            user = User(username=username)

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
                            except Exception as e:
                                logging.error(str(e))
                                raise ValidationError('Saving user `%s` failed.' % username)
                    users.append(user)

        self.queryset = User.objects.all()
        return super(InlineLDAPSearchField, self).clean([u.pk for u in users])