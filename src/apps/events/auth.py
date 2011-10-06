from django.conf                  import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models   import User
from django.core.exceptions       import ImproperlyConfigured
from util                         import LDAPHelper

import logging

log = logging.getLogger(__name__)

class Backend(ModelBackend):
	
	def authenticate(self, username=None, password=None):
		
		try:
			ldap_helper = LDAPHelper()
			LDAPHelper.bind(ldap_helper.connection,username,password)
			ldap_user = LDAPHelper.search_single(ldap_helper.connection,username)
		except LDAPHelper.LDAPHelperException:
			return None
		else:
			# Extract the GUID
			try:

				guid = LDAPHelper.extract_guid(ldap_user)
				user = User.objects.get(profile__guid=guid)
				
				if user.username != username:
					try:
						user.username = username
						user.save()
					except Exception, e:
						log.error('Unable to save user `%s`: %s' % (username,str(e)))
						return None
				
			except LDAPHelper.MissingAttribute:
				return None
			except User.DoesNotExist:

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
					log.error('Unable to save user `%s`: %s' % (username,str(e)))
					return None

		return user
		
	def get_user(self, user_id):
		try:
			return User.objects.get(pk=user_id)
		except User.DoesNotExist:
			return None
