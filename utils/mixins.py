from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _
from django.utils.timezone import now


class LoginRequiredMixin(object):
	def dispatch(self, request, *args, **kwargs):
		if not request.user.is_authenticated():
			raise PermissionDenied
		return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class AutoCreatedUpdatedMixin(models.Model):
	created_at = models.DateTimeField(
		auto_now_add=True,
		blank=False,
		db_index=True,
		editable=False,
		null=False,
		unique=False,
		verbose_name=_('created at'),
	)

	created_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		editable=False,
		on_delete=models.CASCADE,
		related_name="%(class)s_related",
		verbose_name=_('Created by'),
	)

	modified_at = models.DateTimeField(
		auto_now=True,
		editable=False,
		null=True,
		unique=False,
		verbose_name=_('updated at'),
	)

	modified_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		editable=False,
		null=True,
		on_delete=models.CASCADE,
		related_name="%(class)s_related_mod",
		verbose_name=_('Modified by'),
	)

	class Meta:
		abstract = True

	def save(self, *args, **kwargs):
		if 'request' in kwargs and self.user is None:
			request = kwargs.pop('request')
			self.user = request.user
		if self.id or self.created_at:
			auto_updated_at_is_disabled = kwargs.pop('disable_auto_updated_at', False)
			if not auto_updated_at_is_disabled:
				self.modified_at = now()
				if self.user:
					self.modified_by = self.user
		else:
			if self.user:
				self.created_by = self.user
			kwargs['force_insert'] = False
		super(AutoCreatedUpdatedMixin, self).save(*args, **kwargs)


class SoftDeleteMixin(models.Model):
	deleted_at = models.DateTimeField(
		verbose_name=_('deleted at'),
		unique=False,
		null=True,
		blank=True,
		db_index=True,
	)

	class Meta:
		abstract = True

	def delete(self, using=None, keep_parents=False):
		self.deleted_at = now()
		kwargs = {
			'using': using,
		}
		if hasattr(self, 'updated_at'):
			kwargs['disable_auto_updated_at'] = True
		self.save(**kwargs)


class TitleDescriptionModel(models.Model):
	title = models.CharField(blank=False, max_length=255, null=False)
	description = models.TextField(blank=True, null=True)

	class Meta:
		abstract = True


class TitleSlugDescriptionModel(TitleDescriptionModel):
	slug = models.SlugField()

	def save(self, *args, **kwargs):
		if not self.id:
			self.slug = slugify(self.title)
		super(TitleSlugDescriptionModel, self).save(*args, **kwargs)

	class Meta:
		abstract = True


class FullCleanOnSaveMixin(models.Model):
	def save(self, *args, **kwargs):
		self.full_clean()
		super(FullCleanOnSaveMixin, self).save(*args, **kwargs)
