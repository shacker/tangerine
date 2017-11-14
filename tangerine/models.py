from django.db import models
from django.urls import reverse
from django.utils import timezone

from django_extensions.db.models import TimeStampedModel

from users.models import User


POST_TYPE_CHOICES = (
    ('post', 'Post'),
    ('page', 'Page'),
)


class Category(models.Model):
    """Gather Posts in a similar broad topic into Category views."""

    title = models.CharField(max_length=140)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.title


class PostManager(models.Manager):
    """ Filter out all unpublished and trashed posts by calling Post.pub.all() from anywhere. """

    def get_queryset(self):
        return super().get_queryset().filter(published=True, ptype='post', trashed=False).order_by('-created')


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
        help_text="If present, overrides automatic 'created' datetime and will not be published until.",)
    ptype = models.CharField(
        verbose_name='Post or Page',
        choices=POST_TYPE_CHOICES,
        default='post',
        max_length=6,
        help_text="Select Page for semi-static pages. See docs for info.")

    objects = models.Manager()  # The default manager, unfiltered by manager (admin use only)
    pub = PostManager()  # Post.pub.all() gets just published, non-trashed posts

    def get_absolute_url(self):
        # Important to use get_absolute_url in templates rather than `url` tag b/c to avoid 404s due to TZ conversion.
        local_date = timezone.localtime(self.created)
        return reverse('tangerine:post_detail', args=[local_date.year, local_date.month, local_date.day, self.slug])

    def __str__(self):
        return "{d} - {s}".format(d=self.created, s=self.title)


class RelatedLinkGroup(models.Model):
    """ A set of related links (like a Blogroll), orderable in the Admin.
    Tangerine supports multiple RelatedLinkGroups, addressable by slug."""

    # No need for a name - unique slug will do
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.slug


class RelatedLink(models.Model):
    """ Orderable entry in a RelatedLinkGroup. """

    class Meta:
        ordering = ['link_order']

    group = models.ForeignKey(RelatedLinkGroup, on_delete=models.CASCADE)
    site_title = models.CharField(max_length=80, blank=True)
    site_url = models.URLField(null=True)

    # ordering field
    link_order = models.PositiveIntegerField(default=0, editable=False, db_index=True)

    def __str__(self):
        return self.site_title
