from django.contrib.auth.models import AbstractUser
from django.urls import reverse


class User(AbstractUser):
    '''
    Inherits all native User fields from Django and allows adding custom fields (no need for Profile).
    https://docs.djangoproject.com/en/1.11/ref/contrib/auth/#user-model
    '''

    class Meta:
        app_label = 'users'

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse('users:detail', kwargs={'username': self.username})
