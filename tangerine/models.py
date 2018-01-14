from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import make_naive, is_aware

from django_extensions.db.models import TimeStampedModel


POST_TYPE_CHOICES = (
    ('post', 'Post'),
    ('page', 'Page'),
)

# FIXME Also support Disqus, Facebook, other commenting systems?
COMMENT_SYSTEM_CHOICES = (
    ('native', 'Native'),
)


class Config(models.Model):
    """Blog-wide meta/config for a Tangerine installation. Only one instance of this model is allowed."""

    site_title = models.CharField(
        max_length=140,
        default="Arbitrary Site Title",
        help_text="To be displayed in page header and as part of HTML title tag")

    site_url = models.URLField(
        blank=True,
        help_text="Only required for Akismet spam checking")

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

    akismet_key = models.CharField(
        blank=True,
        help_text="For comment spam control (recommended) - get a free/donationware key from https://akismet.com",
        max_length=14
        )

    enable_comments_global = models.BooleanField(
        default=True,
        help_text="Disable to turn off comments site-wide.\
            With global comments enabled, you can still disable comments per-post.)")

    auto_approve_previous_commentors = models.BooleanField(
        default=True,
        help_text="Comments with emails that have been approved before and that pass spam checks\
            will be posted immediately.")

    comment_system = models.CharField(
        choices=COMMENT_SYSTEM_CHOICES,
        default='native',
        max_length=12,
        help_text="Select the commenting system to be used. Tangerine's is \"Native\".")

    from_email = models.CharField(
        default="June Carter-Cash <june@example.com>",
        max_length=100,
        help_text="Emails sent FROM tangerine, such as comment moderation messages, will originate from this address.\
            Should be a real, reachable email."
    )

    moderation_email = models.CharField(
        default="Johnny Cash <johnny@example.com>",
        max_length=100,
        help_text="Comment moderation emails will be sent TO this address.\
            Should be a real, reachable email."
    )

    show_future = models.BooleanField(
        default=False,
        help_text="If enabled, posts dated in the future appear immediately. Default is False (drip-date behavior)."
    )

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
    """ Filter out all unpublished and trashed posts by calling Post.pub.all() from anywhere.
    Filter out future posts if show_future disabled in Config."""

    def get_queryset(self):

        qs = super().get_queryset().filter(published=True, ptype='post', trashed=False).order_by('-pub_date')
        config = Config.objects.first()

        if not config.show_future:
            qs = qs.exclude(pub_date__gt=timezone.now())

        return qs


class Post(TimeStampedModel):
    """ Core definition for a Blog Post"""

    title = models.CharField(max_length=140)

    # slug cannot be used more than once on the same pub_date
    slug = models.SlugField(unique_for_date='pub_date')

    author = models.ForeignKey(
        get_user_model(),  # Replaced by whatever User model is defined for this project
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

    # Used instead of 'created' or 'modified' datetime fields in queries (for editorial control over publication date).
    # Initial pub_date is set in `Post.save()`.
    pub_date = models.DateTimeField(
        verbose_name="Publication Date/Time",
        blank=True,)

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
        # TZ awareness can throw off date resolution when near day boundaries, and generate 404s.
        # If USE_TZ=True in settings, `make_naive` so URL elements always match date elements in `self.pub_date`.
        naive_date = make_naive(self.pub_date) if is_aware(self.pub_date) else self.pub_date
        return reverse(
            'tangerine:post_detail', args=[naive_date.year, naive_date.month, naive_date.day, self.slug])

    def top_level_comments(self):
        # To support threaded commenting, get only top-level comments initially.
        # Get their children in a comment method.
        return self.comment_set.filter(parent__isnull=True, approved=True).order_by('modified')

    def num_comments(self):
        # Return number of all comments for this Post, regardless whether top-level or threaded.
        return self.comment_set.filter(approved=True).count()

    def save(self, *args, **kwargs):
        # Populate pub_date if needed; don't update if already exists.
        if not self.pub_date:
            self.pub_date = timezone.now()
        return super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class CommentManager(models.Manager):
    """ Filter out unapproved comments by calling Comment.pub.all() from anywhere. """

    def get_queryset(self):
        return super().get_queryset().filter(approved=True).order_by('-created')


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
        on_delete=models.CASCADE,
        help_text="ForeignKey to User object; used for authenticated commenters only.")

    # Name and email are non-required so authenticated users can submit comments without entering them;
    # for them, those fields are populated after initial comment save.
    name = models.CharField(
        blank=True,
        max_length=100)
    email = models.EmailField(
        blank=True,
    )
    website = models.URLField(
        blank=True)

    ip_address = models.GenericIPAddressField(
        verbose_name="IP Address",
        blank=True,
        null=True,
        help_text="IP (v4 or v6) of the comment submitter.",
        max_length=24
    )
    user_agent = models.CharField(
        blank=True,
        max_length=160,
        help_text="Reported user-agent string of the comment submitter.")

    body = models.TextField()

    approved = models.BooleanField(default=False)
    spam = models.BooleanField(default=False)  # Check installed spam systems to verify but assume the best

    objects = models.Manager()  # The default manager, unfiltered by manager (admin use only)
    pub = CommentManager()  # Comment.pub.all() gets just approved comments

    def child_comments(self):
        # To support comment threading, return comments that are children of this one.
        return Comment.pub.filter(parent=self).order_by('modified')

    def __str__(self):
        return "{}...".format(self.body[:10])


class ApprovedCommentor(TimeStampedModel):
    """Store emails of approved commentors. If option is enabled, future comments by these
    email addrs will be auto-approved."""

    email = models.EmailField(
        blank=False,
    )

    def __str__(self):
        return self.email


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


def get_author_avatar_upload_dir(instance, filename):
    """Determine upload dir for author avatar image files.
    """

    return '/'.join(['authors', instance.author.username, filename])


class AuthorPage(TimeStampedModel):
    """ Field definitions for Author pages """

    user = models.OneToOneField(
        get_user_model(),  # Replaced by whatever User model is defined for this project
        on_delete=models.CASCADE,
        null=True,
        blank=True)

    about = models.TextField(
        blank=True,
        help_text="Bio/About This Author")

    avatar = models.ImageField(
        upload_to=get_author_avatar_upload_dir,
        help_text="Upload an avatar image to be displayed on your Author page (and possibly elsewhere).",
    )

    def __str__(self):
        return self.user.username
