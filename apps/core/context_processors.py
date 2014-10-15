from django.conf import settings

from events.functions import get_earliest_valid_date
from events.functions import get_latest_valid_date


def get_canonical(request):
    return settings.CANONICAL_ROOT + request.path

def global_settings(request):
	# Return any necessary settings values.
	return {
		'GA_ACCOUNT': settings.GA_ACCOUNT,
		'GOOGLE_WEBMASTER_VERIFICATION': settings.GOOGLE_WEBMASTER_VERIFICATION,
		'FALLBACK_EVENT_DESCRIPTION': settings.FALLBACK_EVENT_DESCRIPTION,
		'CANONICAL_ROOT': settings.CANONICAL_ROOT,
		'CANONICAL_URL': get_canonical(request),
		'EARLIEST_VALID_DATE': get_earliest_valid_date(date_format='%m/%d/%Y'),
		'LATEST_VALID_DATE': get_latest_valid_date(date_format='%m/%d/%Y')
	}