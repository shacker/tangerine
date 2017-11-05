from django.db import models

from adminsortable.fields import SortableForeignKey
from adminsortable.models import SortableMixin

from django_extensions.db.models import TimeStampedModel

from users.models import User


class Category(models.Model):
    """ Gather Posts in a similar broad topic into Category views. """

    title = models.CharField(max_length=140)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.title


class PostManager(models.Manager):
    """ Filter out all unpublished and trashed posts by calling Post.pub.all() from anywhere. """

    def get_queryset(self):
        return super().get_queryset().filter(published=True, trashed=False)


class Post(TimeStampedModel):
    """ Core definition for a Blog Post"""

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
    trashed = models.BooleanField(
        default=False,
        help_text="Trashed posts are removed from views but not deleted. For safety, Trash rather than Delete.")
    categories = models.ManyToManyField(
        Category,
        blank=True,)
    pub_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="If present, overrides automatic 'created' datetime and will not be published until.",
    )

    objects = models.Manager()  # The default manager, unfiltered by manager (admin use only)
    pub = PostManager()  # Post.pub.all() gets just published, non-trashed posts

    def __str__(self):
        return "{d} - {s}".format(d=self.created, s=self.title)


class RelatedLinkGroup(models.Model):
    """ A set of related links (like a Blogroll), orderable in the Admin.
    Tangerine supports multiple RelatedLinkGroups, addressable by slug."""

    # No need for a name - unique slug will do
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.slug


class RelatedLink(SortableMixin):
    """ Orderable entry in a RelatedLinkGroup. """

    class Meta:
        ordering = ['link_order']

    group = SortableForeignKey(RelatedLinkGroup, on_delete=models.CASCADE)
    site_title = models.CharField(max_length=80, blank=True)
    site_url = models.URLField(null=True)

    # ordering field
    link_order = models.PositiveIntegerField(default=0, editable=False, db_index=True)

    def __str__(self):
        return self.site_title
