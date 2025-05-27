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
    nid = saml_data['http://schemas.xmlsoap.org/ws/2005/05/identity/claims/NID'][0]
    user = None
    try:
        user = User.objects.get(username=nid.strip())
    except User.DoesNotExist:
        logging.warning(f"User not found: {nid}")
        pass
    except Exception as e:
        logging.error(f"Error: {e}")

    logging.info(user)

    return user
