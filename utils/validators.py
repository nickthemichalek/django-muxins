from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from base64 import b32decode
import binascii


def validate_base32(string):
	try:
		b32decode(string)
	except binascii.Error:
		raise ValidationError(_('%(string)s is not a valid base32 encoded string'), params={'value': string})
