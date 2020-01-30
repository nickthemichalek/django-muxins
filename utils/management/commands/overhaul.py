from django.core.management.base import BaseCommand
from django.core import management

from django.conf import settings
from django.contrib.auth import get_user_model;

import os
import shutil


class Command(BaseCommand):
	def remove_database_file(self):
		path = settings.DATABASES['default']['NAME']
		print(path)
		if os.path.isdir(path) and not os.path.islink(path):
			shutil.rmtree(path)
		if os.path.exists(path):
			os.remove(path)

	def create_admin_user(self):
		User = get_user_model()
		User.objects.create_superuser('admin@admin.com', 'admin')

	def handle(self, **options):
		if settings.DEBUG:
			self.remove_database_file()
			# Delete everything except __init__.py file from migration folder in all django apps (use OWN_APPS)
			management.call_command('makemigrations', interactive=False)
			management.call_command('migrate', interactive=False, run_syncdb=True)
			self.create_admin_user()
