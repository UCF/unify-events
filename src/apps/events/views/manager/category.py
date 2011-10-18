from events.forms.manager           import CategoryForm
from events.models                  import Category
from django.contrib                 import messages
from django.http                    import HttpResponseNotFound, HttpResponseForbidden,HttpResponseRedirect
from django.core.urlresolvers       import reverse
from django.views.generic.simple    import direct_to_template
from django.contrib.auth.decorators import login_required
import logging

log = logging.getLogger(__name__)


@login_required
def create_update(request, id=None):
	ctx  = {'category':None,'form':None,'mode':'create'}
	tmpl = 'events/manager/category/create_update.html'

	if not request.user.is_superuser:
		return HttpResponseForbidden('Only super users can create or update categories.')

	if id is not None:
		try:
			ctx['category'] = category.objects.get(pk=id)
		except Category.DoesNotExist:
			return HttpResponseNotFound('category specified does not exist.')
		else:
			ctx['mode'] = 'update'

	if request.method == 'POST':
		ctx['form'] = CategoryForm(request.POST,instance=ctx['category'])
		if ctx['form'].is_valid():
			try:
				category = ctx['form'].save()
			except Exception, e:
				log.error(str(e))
				message.error(request, 'Saving category failed.')
			else:
				messages.success(request, 'category saved successfully.')
			return HttpResponseRedirect(reverse('dashboard'))
	else:
		ctx['form'] = CategoryForm(instance=ctx['category'])

	return direct_to_template(request,tmpl,ctx)

@login_required
def delete(request, id):
	try:
		category = Category.objects.get(pk=id)
	except Category.DoesNotExist:
		return HttpResponseNotFound('category specified does not exist.')
	else:
		if not request.user.is_superuser:
			return HttpResponseForbidden('You cannot modify the specified category.')
		else:
			try:
				for event in category.events.all():
					event.categorys.remove(category)
				category.delete()
			except Exception, e:
				log.error(str(e))
				messages.error(request, 'Deleting category failed.')
			else:
				messages.success(request, 'category successfully deleted.')
			return HttpResponseRedirect(reverse('dashboard'))

@login_required
def merge(request, from_id, to_id):
	try:
		from_category = Category.objects.get(pk=from_id)
		to_category   = Category.objects.get(pk=to_id)
	except Category.DoesNotExist:
		return HttpResponseNotFound('category specified does not exist')
	else:
		if not request.user.is_superuser:
			return HttpResponseForbidden('You cannot modify the specified category.')
		else:
			try:
				for event in from_category.events.all():
					event.categories.add(to_category)
				for event in from_category.events.all():
					event.categories.remove(from_category)
				from_category.delete()
			except Exception, e:
				log.error(str(e))
				messages.error(request, 'Merging categorys failed.')
			else:
				messages.success(request, 'categorys successfully merged.')
			return HttpResponseRedirect(reverse('dashboard'))

@login_required
def manage(request):
	ctx  = {'categorys':None}
	tmpl = 'events/manager/category/manage.html'

	if not request.user.is_superuser:
		return HttpResponseForbidden('You cannot manage categorys.')

	ctx['categorys'] = Category.objects.all()

	return direct_to_template(request,tmpl,ctx)
