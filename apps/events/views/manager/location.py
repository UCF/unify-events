import logging

from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.simple import direct_to_template

from events.forms.manager import LocationForm
from events.models import Location

log = logging.getLogger(__name__)


@login_required
def list(request, state=None):
    """
    View for listing out the locations.
    """
    if not request.user.is_superuser:
        return HttpResponseForbidden('You cannot views locations.')

    ctx = {
        'state': None,
        'locations': None,
        'review_count': Location.objects.filter(reviewed=False).count(),
    }

    tmpl = 'events/manager/location/list.html'

    if state is not None and state in ['review', 'approved']:
        ctx['state'] = state
        if state == 'review':
            ctx['locations'] = Location.objects.filter(reviewed=False)
        else:
            ctx['locations'] = Location.objects.filter(reviewed=True)
    else:
        ctx['locations'] = Location.objects.all()

    return direct_to_template(request, tmpl, ctx)

@login_required
def create_update(request, location_id=None):
    """
    View for creating and updating the location.
    """
    ctx = {'location': None, 'form': None, 'mode': 'create'}
    tmpl = 'events/manager/location/create_update.html'

    if not request.user.is_superuser:
        return HttpResponseForbidden('You cannot create/modify a location.')

    if location_id:
        ctx['mode'] = 'update'
        ctx['location'] = get_object_or_404(Location, pk=location_id)

    if request.method == 'POST':
        ctx['form'] = LocationForm(request.POST, instance=ctx['location'])
        if ctx['form'].is_valid():
            try:
                ctx['form'].save()
            except Exception, e:
                log.error(str(e))
                messages.error(request, 'Saving location failed.')
            return HttpResponseRedirect(reverse('location-list'))
    else:
        ctx['form'] = LocationForm(instance=ctx['location'])
    return direct_to_template(request, tmpl, ctx)
