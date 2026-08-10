"""``TRIGGER`` hooks for django-saml2-auth.

The package's own ``_create_new_user`` populates fields from ``ATTRIBUTES_MAP``
(which is keyed by the full claim URI). These hooks additionally sync from the
friendly attribute names pysaml2 resolves, and run on every login so that a
name or email change in the IdP propagates to an existing account.
"""
from django.contrib.auth.models import User


def _first(saml_data, *keys):
    """Return the first value present under any of ``keys``, or ''.

    Claims arrive as lists. A missing claim must not raise -- an incomplete
    assertion should degrade to a partially populated user, not a 500 at the
    ACS step.
    """
    for key in keys:
        values = saml_data.get(key)
        if values:
            return values[0]
    return ''


def _sync_user(user, saml_data):
    user.first_name = _first(saml_data, 'givenName') or user.first_name
    user.last_name = _first(saml_data, 'surname') or user.last_name
    user.email = _first(saml_data, 'emailAddress') or user.email
    user.save()


def on_saml_user_create(user: User, saml_data: dict):
    _sync_user(user, saml_data)


def on_saml_before_login(user: User, saml_data: dict):
    _sync_user(user, saml_data)
