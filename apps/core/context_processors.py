from django.conf import settings

def global_settings(request):
	# Return any necessary settings values.
	return {
		'GA_ACCOUNT': settings.GA_ACCOUNT
	}