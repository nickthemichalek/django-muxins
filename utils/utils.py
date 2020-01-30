import datetime

from django.core.exceptions import ValidationError
# from pattern.en import pluralize, singularize

from functools import lru_cache

from django.core.management.utils import get_random_secret_key


def join_if_not_None(prefix, x):
	return prefix + ' ' + str(x) if x else ''


def raise_validation_error_if_false(err, f, *args):
	if not f(*args):
		raise ValidationError(err)


def type_error_if_not_of_type(expected_type, actual, err=None):
	if type(actual) is not expected_type:
		raise TypeError('Parameter must be of type ' + expected_type.__name__ if not err else err)


def timedelta_to_hours_minutes(td):
	type_error_if_not_of_type(datetime.timedelta, td)
	return td.seconds // 3600, (td.seconds // 60) % 60


def time_to_minutes(t: datetime.time):
	type_error_if_not_of_type(datetime.time, t)
	return t.hour * 60 + t.minute


def time_to_todays_datetime(t):
	type_error_if_not_of_type(datetime.time, t)
	return datetime.datetime.combine(datetime.date.today(), t)


@lru_cache(maxsize=None)
def pluralise_if_needed(word, n):
	# return pluralize(word) if n > 1 else singularize(word)
	return word + 's' if n > 1 else word


def duration_to_str(hours, minutes):
	if hours < 0 or minutes < 0:
		raise ValueError('hours and minutes must not be negative')

	if hours == 0 and minutes == 0:
		raise ValueError('hours and minutes cannot both be zero')

	hours += minutes // 60
	minutes = minutes % 60

	hours_str = str(hours)
	minutes_str = str(minutes)

	if minutes == 30:
		return {
			0: 'half an hour',
			1: 'an hour and a half'
		}.get(hours, hours_str + ' and a half hours')

	# minutes != 30, hours and minutes > 0

	hours_str += ' ' + pluralise_if_needed('hour', hours)
	minutes_str += ' ' + pluralise_if_needed('minute', minutes)

	if hours == 0:
		return minutes_str

	return hours_str + ' and ' + minutes_str


def comma_separated_strings_from_objects(l):
	return ", ".join([str(o) for o in l])


def date_of_past_or_current_weekday(weekday, date=datetime.datetime.today()):
	return (date - datetime.timedelta(days=weekday)).date()


def date_of_upcoming_weekday(weekday, date=datetime.datetime.today()):
	ahead = weekday - date.weekday()
	return date + datetime.timedelta(days=ahead, weeks=1 if ahead <= 0 else 0)


def date_of_upcoming_monday():
	return date_of_upcoming_weekday(0)


def date_of_upcoming_sunday():
	return date_of_upcoming_weekday(6)


def date_of_upcoming_sunday_after_next_monday():
	return date_of_upcoming_sunday() + datetime.timedelta(weeks=1)


def date_of_last_monday():
	return date_of_past_or_current_weekday(0)


def current_week(week_starts_on_sunday=False):
	# defined as range from past monday and the following sunday
	pass


def date_to_datetime(d: datetime.date) -> datetime.datetime:
	return datetime.datetime.combine(d, datetime.datetime.min.time())


def filter_dict_by_keys(d: dict, keys: list) -> dict:
	'''filtered = {}
	for key in keys:
		if key in d:
			filtered[key] = d[key]
	return filtered'''
	return {key: d[key] for key in d if key in keys}


def filter_dict_by_key(d: dict, key) -> dict:
	return filter_dict_by_keys(d, [key])


def ignore_keys_in_dict(d: dict, keys: list) -> dict:
	return {key: d[key] for key in d if key not in keys}


def generate_secret_key(path):
	secret_key = get_random_secret_key()
	with open(path, 'w') as f:
		f.write('SECRET_KEY = \'{}\''.format(secret_key))
		f.close()
