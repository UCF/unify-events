"""Project overrides for the django-saml2-auth ``signin`` and ``acs`` views.

The upstream package (``django_saml2_auth``) round-trips the post-login
return URL through ``request.session["login_next_url"]``. That fails for the
ACS step because Azure POSTs the SAMLResponse to ``/sso/acs/`` as a
cross-site, top-level request, and ``SameSite=Lax`` session cookies are not
sent on such requests -- so the return URL is lost and the user falls back to
``DEFAULT_NEXT_URL``.

These wrappers instead carry the return URL in the SAML ``RelayState``, which
the IdP echoes back verbatim, independent of any cookie. The session key is
still populated as a same-site fallback and so the upstream ``acs`` view can
be reused unchanged.
"""
import urllib.parse as _urlparse
from urllib.parse import unquote

from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    HttpResponseServerError,
)
from django.views.decorators.csrf import csrf_exempt

from django_saml2_auth import views as saml
from django_saml2_auth.views import (
    BINDING_HTTP_POST,
    BINDING_HTTP_REDIRECT,
    _get_saml_client,
    denied,
    get_current_domain,
    get_default_next_url,
    get_reverse,
    is_safe_url,
)


def _denied_response():
    return HttpResponseRedirect(
        get_reverse([denied, "denied", "django_saml2_auth:denied"])
    )


def _resolve_next_url(request):
    """Return a validated ``next`` URL from the request, or ``None`` if unsafe.

    Mirrors the upstream ``signin`` handling, including unwrapping a nested
    ``?next=`` that Django's ``LoginView`` produces.
    """
    next_url = request.GET.get("next", get_default_next_url())

    try:
        if "next=" in unquote(next_url):
            next_url = _urlparse.parse_qs(
                _urlparse.urlparse(unquote(next_url)).query
            )["next"][0]
    except (KeyError, IndexError, TypeError, ValueError):
        next_url = request.GET.get("next", get_default_next_url())

    if not is_safe_url(next_url, None):
        return None
    return next_url


def signin(request):
    """Initiate SAML auth, carrying the return URL in ``RelayState``."""
    next_url = _resolve_next_url(request)
    if next_url is None:
        return _denied_response()

    # Keep the session value as a same-site fallback (e.g. IdP-initiated flows
    # where RelayState may be absent).
    request.session["login_next_url"] = next_url

    sp_settings = (
        saml.settings.SAML2_AUTH.get("SAML_CLIENT_SETTINGS", {})
        .get("service", {})
        .get("sp", {})
    )
    idp_entity_id = sp_settings.get("idp")
    binding = sp_settings.get("binding", BINDING_HTTP_REDIRECT)

    saml_client = _get_saml_client(get_current_domain(request))
    _, info = saml_client.prepare_for_authenticate(
        idp_entity_id, relay_state=next_url, binding=binding
    )

    if binding == BINDING_HTTP_REDIRECT:
        redirect_url = dict(info.get("headers", [])).get("Location")
        if not redirect_url:
            return HttpResponseServerError(
                "Missing redirect Location header from SAML client"
            )
        return HttpResponseRedirect(redirect_url)
    elif binding == BINDING_HTTP_POST:
        return HttpResponse(info["data"])
    return HttpResponseServerError(f"SSO binding not supported: {binding}")


@csrf_exempt
def acs(request):
    """Consume the SAML response, preferring ``RelayState`` for the redirect.

    The upstream ``acs`` reads ``session["login_next_url"]``; we seed that key
    from the (re-validated) RelayState the IdP echoed back, then delegate.
    """
    relay_state = request.POST.get("RelayState")
    if relay_state and is_safe_url(relay_state, None):
        request.session["login_next_url"] = relay_state

    return saml.acs(request)
