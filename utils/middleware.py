from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden
from django.utils.timezone import now


class BlockedIpMiddleware(object):
	def process_request(self, request):
		if request.META['REMOTE_ADDR'] in settings.BLOCKED_IPS:
			return HttpResponseForbidden('<h1>Forbidden</h1>')
		return None


class SetLastVisitMiddleware(object):
	def process_response(self, request, response):
		if request.user.is_authenticated():
			# Update last visit time after request finished processing.
			get_user_model().objects.filter(pk=request.user.pk).update(last_visit=now())
		return response


class TimezoneMiddleware(object):
	def process_request(self, request):
		# Assuming user has a OneToOneField to a model called Profile
		# And Profile stores the timezone of the User.
		request.session['timezone'] = request.user.profile.timezone
