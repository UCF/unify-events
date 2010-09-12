from django.shortcuts import render_to_response as _r2r
from django.template  import RequestContext

def render_to_response(
		request,
		template,
		dictionary={},
		context_instance=None,
		mimetype=None
	):
	rc = RequestContext(request)
	return _r2r(
		template,
		dictionary=dictionary,
		context_instance=context_instance,
		mimetype=mimetype
	)