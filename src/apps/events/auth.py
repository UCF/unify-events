from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_model
import ldap
import logging

log = logging.getLogger(__name__)

class Backend(ModelBackend):
  user_model = 'events.User'
  
  def authenticate(self, username=None, password=None):
    # Bind to the NET DOMAIN with credentials
    ldap_username = '@'.join([username,'net.ucf.edu'])
    try:
      ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
      ldap.set_option(ldap.OPT_REFERRALS, 0)
      ldap_obj = ldap.initialize(settings.LDAP_NET_HOST)
      ldap_obj.simple_bind_s(ldap_username,password)
    except ldap.INVALID_CREDENTIALS:
      log.info('Invalid credentials for `%s`' % username)
    except ldap.LDAPError, e:
      log.error('LDAP Error: %s' % str(e))
    else:
      # Search for the user
      ldap_result_set = []
      try:
        
        result_id = ldap_obj.search(settings.LDAP_NET_BASE_DN,ldap.SCOPE_SUBTREE, 'cn=%s' % username,None)
        while 1:
          result_type, result_data = ldap_obj.result(result_id, 0)
          if (result_data == []):
            break
          else:
            if result_type == ldap.RES_SEARCH_ENTRY:
              ldap_result_set.append(result_data)
      except ldap.LDAPError, e:
        log.error('LDAP Error: %s' % str(e))
      else:
        if len(ldap_result_set) == 0:
          log.error('LDAP Search returned no users')
        elif len(ldap_result_set) > 1:
          log.error('LDAP Search returned more than 1 user')
        else:
          try:
            ldap_user = ldap_result_set[0][0][1]
          except ValueError:
            log.error('LDAP response in an unknown form')
          else:
            try:
              ldap_guid = ldap_user['objectGUID']
            except KeyError:
              log.error('LDAP GUID not present for `%s`' % username)
            else:
              try:
                user = self.user_class.objects.get(ldap_guid=ldap_guid)
              except self.user_class.DoesNotExist:
                user = self.user_class(ldap_guid = ldap_guid)
              else:
                for ldap_attr,user_attr in settings.LDAP_NET_ATTR_MAP.items():
                  try:
                    setattr(user, user_attr, ldap_user[ldap_attr])
                  except KeyError:
                    log.error('LDAP attribute `%s` not set for user `%s`' % (ldap_attr,username))
                return user
        return None
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
