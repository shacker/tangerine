from django.db import models

from django_extensions.db.models import TimeStampedModel

from users.models import User


class Post(TimeStampedModel):

    # timestamp inherited from TimeStampedModel
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True)
    subject = models.CharField(
        max_length=255,
        default="No subject")
    content = models.TextField(
        blank=True,)

    def __str__(self):
        return "{s}".format(s=self.subject)
