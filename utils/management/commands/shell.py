import sys
import os
from optparse import make_option
from django.core.management.commands.shell import Command as DjangoShellCommand
from django.db import router
from django.core.management.base import BaseCommand

_original_db_for_write = None


def confirm_writable(self, *args, **kwargs):
	''' user can over-ride the shell to be writable at any time, but it sends a message '''

	# for migrations, you might be in a non-interactive shell
	# so don't prompt, but still send out the notification
	if sys.stdin.isatty():
		cont = input('Are you sure you want to connect to the production database in writable mode? [y/N] ')
		if not cont.lower().startswith('y'):
			raise IOError('Database in read-only mode.')

	router.db_for_write = _original_db_for_write
	send_alert()


def send_alert():
	#hipchat.send_message("I'm opening up a writable prod shell!", from_name=os.environ.get('USER'), color='red')
	print("write enabled for shell!")

class Command(BaseCommand):
	option_list = DjangoShellCommand.option_list + (
		make_option('--write', action='store_true', dest='writable',
					help='Connect to the database in writable mode.'),
	)

	def handle(self, *args, **options):
		self.handle_noargs(options)

	def handle_noargs(self, **options):
		# only allow read-only shells in prod by default
		if options.get('writable'):
			send_alert()
		else:
			global _original_db_for_write
			_original_db_for_write = router.db_for_write
			router.db_for_write = confirm_writable

		return super(Command, self).handle_noargs(**options)
