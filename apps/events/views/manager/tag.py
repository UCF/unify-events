from events.forms.manager import TagForm
from events.models import Tag
from django.contrib import messages
from django.http import HttpResponseNotFound, HttpResponseForbidden,HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required
import logging

log = logging.getLogger(__name__)


@login_required
def create_update(request, id=None):
    ctx = {'tag': None, 'form': None,'mode': 'create'}
    tmpl = 'events/manager/tag/create_update.html'

    if id is not None:
        try:
            ctx['tag'] = Tag.objects.get(pk=id)
        except Tag.DoesNotExist:
            return HttpResponseNotFound('Tag specified does not exist.')
        else:
            ctx['mode'] = 'update'
            if not request.user.is_superuser:
                return HttpResponseForbidden('You cannot modify the specified tag.')

    if request.method == 'POST':
        ctx['form'] = TagForm(request.POST,instance=ctx['tag'])
        if ctx['form'].is_valid():
            try:
                tag = ctx['form'].save()
            except Exception, e:
                log.error(str(e))
                message.error(request, 'Saving tag failed.')
            else:
                messages.success(request, 'Tag saved successfully.')
            return HttpResponseRedirect(reverse('dashboard'))
    else:
        ctx['form'] = TagForm(instance=ctx['tag'])

    return direct_to_template(request,tmpl,ctx)

@login_required
def delete(request, id):
    try:
        tag = Tag.objects.get(pk=id)
    except Tag.DoesNotExist:
        return HttpResponseNotFound('Tag specified does not exist.')
    else:
        if not request.user.is_superuser:
            return HttpResponseForbidden('You cannot modify the specified tag.')
        else:
            try:
                for event in tag.events.all():
                    event.tags.remove(tag)
                tag.delete()
            except Exception, e:
                log.error(str(e))
                messages.error(request, 'Deleting tag failed.')
            else:
                messages.success(request, 'Tag successfully deleted.')
            return HttpResponseRedirect(reverse('dashboard'))

@login_required
def merge(request, from_id, to_id):
    try:
        from_tag = Tag.objects.get(pk=from_id)
        to_tag = Tag.objects.get(pk=to_id)
    except Tag.DoesNotExist:
        return HttpResponseNotFound('Tag specified does not exist')
    else:
        if not request.user.is_superuser:
            return HttpResponseForbidden('You cannot modify the specified tag.')
        else:
            try:
                for event in from_tag.events.all():
                    event.tags.add(to_tag)
                for event in from_tag.events.all():
                    event.tags.remove(from_tag)
                from_tag.delete()
            except Exception, e:
                log.error(str(e))
                messages.error(request, 'Merging tags failed.')
            else:
                messages.success(request, 'Tags successfully merged.')
            return HttpResponseRedirect(reverse('dashboard'))

@login_required
def manage(request):
    ctx = {'tags': None}
    tmpl = 'events/manager/tag/manage.html'

    if not request.user.is_superuser:
        return HttpResponseForbidden('You cannot manage tags.')

    ctx['tags'] = Tag.objects.all()

    return direct_to_template(request,tmpl,ctx)
