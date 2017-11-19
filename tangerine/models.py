from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone

from django_extensions.db.models import TimeStampedModel

from users.models import User


POST_TYPE_CHOICES = (
    ('post', 'Post'),
    ('page', 'Page'),
)

# FIXME Also support Disqus, Facebook, other commenting systems?
COMMENT_TYPE_CHOICES = (
    ('native', 'Native'),
)


class Config(models.Model):
    """Blog-wide meta/config for a Tangerine installation. Only one instance of this model is allowed."""

    site_title = models.CharField(
        max_length=140,
        default="Arbitrary Site Title",
        help_text="To be displayed in page header and as part of HTML title tag")

    tagline = models.CharField(
        max_length=140,
        blank=True,
        default='',
        help_text="Optional pithy descriptive phrase")

    num_posts_per_list_view = models.SmallIntegerField(
        verbose_name="Number of Posts Per List View",
        default=10,
        help_text="Used on default homepage, categories, date archives, etc.)")

    google_analytics_id = models.CharField(
        blank=True,
        help_text="Enter just the GA tracking ID provided by Google, not the entire codeblock, e.g UA-123456-2.",
        max_length=16
        )

    enable_comments_global = models.BooleanField(
        default=True,
        help_text="Disable to turn off comments site-wide.\
            With global comments enabled, you can still disable comments per-post.)")

    comment_system = models.CharField(
        choices=COMMENT_TYPE_CHOICES,
        default='native',
        max_length=12,
        help_text="Select the commenting system to be used. Tangerine's is \"Native\".")

    class Meta:
        verbose_name_plural = "Config"

    def save(self, *args, **kwargs):
        # Allow only one instance of the Config model
        if Config.objects.exists() and not self.pk:
            raise ValidationError('There can be only one Config instance')
        return super(Config, self).save(*args, **kwargs)

    def __str__(self):
        return self.site_title


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

    enable_comments = models.BooleanField(
        default=True,
        help_text="Disable to turn off comments for this Post/Page only.\
            Overriden if Global Comment Enable is off in Config.")

    objects = models.Manager()  # The default manager, unfiltered by manager (admin use only)
    pub = PostManager()  # Post.pub.all() gets just published, non-trashed posts

    def get_absolute_url(self):
        # Important to use get_absolute_url in templates rather than `url` tag b/c to avoid 404s due to TZ conversion.
        local_date = timezone.localtime(self.created)
        return reverse('tangerine:post_detail', args=[local_date.year, local_date.month, local_date.day, self.slug])

    def __str__(self):
        return self.title


class Comment(TimeStampedModel):
    """ Core definition for a comment. Each comment has a required FK to a Post and an optional FK to
    another comment (threaded commenting support). Only approved comments are shown on-page.
    Moderator can permanently approve email addresses. See `post_detail` and moderation module
    for approval logic.
    """

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE)

    parent = models.ForeignKey(
        'self',
        verbose_name="Parent comment",
        blank=True,
        null=True,
        on_delete=models.CASCADE)

    author = models.ForeignKey(
        get_user_model(),
        blank=True,
        null=True,
        on_delete=models.CASCADE)

    name = models.CharField(
        blank=True,
        max_length=100)
    website = models.URLField(
        blank=True)
    email = models.EmailField(
        blank=True,
    )

    body = models.TextField()

    approved = models.BooleanField(default=False)

    def __str__(self):
        return "{}...".format(self.body[:10])


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
