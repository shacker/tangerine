from django.db import models

from django_extensions.db.models import TimeStampedModel

from users.models import User


class Category(models.Model):
    title = models.CharField(max_length=140)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.title


class PostManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(published=True)


class Post(TimeStampedModel):

    title = models.CharField(max_length=140)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True)
    summary = models.TextField(
        blank=True,)
    content = models.TextField(
        blank=True,)
    published = models.BooleanField(default=True)
    categories = models.ManyToManyField(
        Category,
        blank=True,)
    pub_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="If present, overrides automatic 'created' datetime and will not be published until.",
    )

    objects = models.Manager()  # The default manager, unfiltered by manager (admin use only)
    pub = PostManager()  # Post.pub () gets just published posts

    def __str__(self):
        return "{d} - {s}".format(d=self.created, s=self.title)
