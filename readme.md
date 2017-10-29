
Be sure to set your timezone in settings:
TIME_ZONE = 'America/Los_Angeles'
You can list all the available timezones with pytz.all_timezones:
import pytz
pytz.all_timezones


# After creating some categories manually, use this to create 500 faked posts for testing purposes
from blog.factories import PostFactory
PostFactory.create_batch(500)
