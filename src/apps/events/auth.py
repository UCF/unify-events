from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_model
from util import LDAPHelper

import logging

log = logging.getLogger(__name__)

class Backend(ModelBackend):
  user_model = 'events.User'
  
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
        user = self.user_class.objects.get(ldap_guid=guid)
        
        if user.username != username:
          try:
            user.username = username
            user.save()
          except Exception, e:
            log.error('Unable to save user `%s`: %s' % (username,str(e)))
            return None
        
      except ValueError:
        return None
      except self.user_class.DoesNotExist:
        user = self.user_class(username=username,ldap_guid=guid)
        
        # Try to extract some other details
        try:               user.first_name = LDAPHelper.extract_firstname(ldap_user)
        except ValueError: pass
        try:               user.last_name = LDAPHelper.extract_lastname(ldap_user)
        except ValueError: pass
        try:               user.email = LDAPHelper.extract_email(ldap_user)
        except ValueError: pass
        
        try:
          user.save()
        except Exception, e:
          log.error('Unable to save user `%s`: %s' % (username,str(e)))
          return None
          
    return user
    
  def get_user(self, user_id):
    try:
      return self.user_class.objects.get(pk=user_id)
    except self.user_class.DoesNotExist:
      return None
  
  @property
  def user_class(self):
    if not hasattr(self, '_user_class'):
      self._user_class = get_model(*self.user_model.split('.', 2))
      if not self._user_class:
        raise ImproperlyConfigured('Could not get custom user model')
    return self._user_class
