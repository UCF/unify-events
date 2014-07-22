from django.conf import settings

def get_canonical(request):
    return settings.CANONICAL_ROOT + request.path

def global_settings(request):
	# Return any necessary settings values.
	return {
		'GA_ACCOUNT': settings.GA_ACCOUNT,
		'FALLBACK_EVENT_DESCRIPTION': settings.FALLBACK_EVENT_DESCRIPTION,
		'CANONICAL_ROOT': settings.CANONICAL_ROOT,
		'CANONICAL_URL': get_canonical(request)
	}