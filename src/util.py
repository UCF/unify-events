from django.conf import settings
import logging
import ldap

class LDAPHelper(object):
  
  _log = logging.getLogger(__name__)
  
  class LDAPHelperException(Exception):
    def __init__(self, error = 'No addtional information'):
      LDAPHelper._log.error(': '.join([str(self.__doc__),str(self.error)]))
      
  class UnableToConnect(LDAPHelperException):
    '''Unable to Connect'''
    pass
  class UnableToBind(LDAPHelperException):
    '''Unable to Bind'''
    pass
  class UnableToSearch(LDAPHelperException):
    '''Unable to Search'''
    pass
  class MultipleUsersFound(LDAPHelperException):
    '''Single search returned more than one'''
    pass
  class NoUsersFound(LDAPHelperException):
    '''Search did not find any users'''
    pass
  class UnexceptedResultForm(LDAPHelperException):
    '''Search result was in an unexpected'''
    pass
  
  def __init__(self):
    self.connection = LDAPHelper.connect()
    
  @classmethod
  def connect(cls):
    try:
      # TODO - Figure out why we have to ignore the cert check here
      ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
      ldap.set_option(ldap.OPT_REFERRALS, 0)
      return ldap.initialize(settings.LDAP_NET_HOST)
    except ldap.LDAPError, e:
      raise LDAPHelper.UnableToConnect(e)
  
  @classmethod
  def bind(cls,connection,username,password):
    try:
      connection.simple_bind_s(username + settings.LDAP_NET_USER_SUFFIX,password)
    except ldap.LDAPError, e:
      raise LDAPHelper.UnableToBind(e)
      
  @classmethod
  def search_single(cls,connection,username):
    results = []
    try:
      result_id = connection.search(settings.LDAP_NET_BASE_DN,ldap.SCOPE_SUBTREE,'cn=%s' % username,None)
    except ldap.LDAPError, e:
      raise LDAPHelper.UnableToSearch(e)
    else:
      while 1:
        type, data = connection.result(result_id, 0)
        if (data == []):
          break
        else:
          if type == ldap.RES_SEARCH_ENTRY:
            results.append(data)
      if len(results) == 0:
        raise LDAPHelper.NoUsersFound()
      elif len(results) > 1:
        raise LDAPHelper.MultipleUsersFound(e)
      else:
        try:
          return results[0][0][1]
        except ValueError:
          raise LDAPHelper.UnexpectedResultForm(e)
    
  @classmethod
  def extract_guid(self,ldap_user):
    return ldap_user['objectGUID']
  
  @classmethod
  def extract_firstname(self,ldap_user):
    return ldap_user['givenName']
    
  @classmethod
  def extract_lastname(self,ldap_user):
    return ldap_user['sn']
    
  @classmethod
  def extract_email(self,ldap_user):
    return ldap_user['mail']