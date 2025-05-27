from django.contrib.auth.models import User

import logging

def on_saml_user_create(user: User, saml_data: dict):
    user.first_name = saml_data['givenName'][0]
    user.last_name = saml_data['surname'][0]
    user.email = saml_data['emailAddress'][0]
    user.save()

def on_saml_before_login(user: User, saml_data: dict):
    user.first_name = saml_data['givenName'][0]
    user.last_name = saml_data['surname'][0]
    user.email = saml_data['emailAddress'][0]
    user.save()

def on_saml_find_user(saml_data: dict) -> User:
    guid = saml_dict['http://schemas.microsoft.com/identity/claims/objectidentifier'][0]
    user = None
    try:
        user = User.objects.get(profile__guid=guid.strip())
    except User.DoesNotExist:
        logging.warning(f"User not found: {guid}")
        pass
    except Exception as e:
        logging.error(f"Error: {e}")

    logging.info(user)

    return user
