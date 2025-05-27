from django.contrib.auth.models import User

import logging

def on_saml_user_create(user: User, saml_data: dict):
    logging.info(saml_data)
    user.first_name = saml_data['givenName'][0]
    user.last_name = saml_data['surname'][0]
    user.email = saml_data['emailAddress'][0]
    user.save()

def on_saml_before_login(user: User, saml_data: dict):
    logging.info(saml_data)
    user.first_name = saml_data['givenName'][0]
    user.last_name = saml_data['surname'][0]
    user.email = saml_data['emailAddress'][0]
    user.save()
