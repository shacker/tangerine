from ipware.ip import get_ip
import akismet
import bleach

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Q
from django.template.loader import render_to_string

from tangerine.models import ApprovedCommentor, Blog, Comment, Post


def sanitize_comment(comment):
    """Sanitize malicious tags from posted comments.
    Takes an HTML comment string, returns that comment with malicious tags removed.
    Defaults to bleach's default set of allowed tags:
    ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'strong', 'ul']
    but can be overriden by adding to settings e.g.:
    BLEACH_ALLOWED_TAGS = ['hr', 'b', 'i']
    """

    if hasattr(settings, 'BLEACH_ALLOWED_TAGS'):
        allowed_tags = settings.BLEACH_ALLOWED_TAGS
    else:
        allowed_tags = bleach.sanitizer.ALLOWED_TAGS

    return bleach.clean(comment, tags=allowed_tags, strip=True)


def get_comment_approval(email, authenticated):
    """Comment approval workflow.
    `auto_approve` doesn't mean blanket approval, but "IF email is in ApprovedCommentor table".
    Authenticated commenters are always allowed to comment without moderation."""

    config = Blog.objects.first()
    auto_approve = config.auto_approve_previous_commentors

    if (
        authenticated or
            (auto_approve and ApprovedCommentor.objects.filter(email=email).exists())
    ):
        return True
    else:
        return False


def toggle_approval(comment):
    """Toggle comment approval

    Takes a comment, returns nothing.

    If input comment was unapproved, approve it (and vice versa).

    If auto_approve is enabled in Blog config and comment is approved, also add user to ApprovedCommentors,
    (or remove if unapproving)."""

    config = Blog.objects.first()
    auto_approve = config.auto_approve_previous_commentors

    if auto_approve:
        if comment.approved:
            # Toggling state for an approved comment, so we now remove commenter from ApprovedCommentors
            ApprovedCommentor.objects.filter(email=comment.email).delete()
        else:
            # Toggling state for an unapproved comment, so we now add commenter to ApprovedCommentors
            ApprovedCommentor.objects.create(email=comment.email)

    # Then flip comment approval state to the opposite of whatever it is now.
    comment.approved = not comment.approved
    comment.save()


def send_comment_moderation_email(comment):
    """Alert post author that comment needs moderation, or has been automatically published.
    Comments need moderation if they are marked as spam or not set to auto-approve.

    Takes a comment object, returns nothing"""

    config = Blog.objects.first()

    if comment.spam or not comment.approved:
        # send moderation email
        subject = "A new comment on {} requires moderation".format(config.site_title)
    else:
        # send announcement email
        subject = "A new comment on {} has been automatically published".format(config.site_title)

    send_mail(
        subject,
        render_to_string('tangerine/email/comment_moderation.txt', {'config': config, 'comment': comment}),
        config.from_email,
        [config.moderation_email, ],
        fail_silently=True
    )


def process_comment(request, comment, post):
    """Set attributes, spam check, get IP address, sanitize, etc. No return value."""

    if request.user.is_authenticated:
        # We already set auth user's name and email in the form's inital vals.
        comment.author = request.user

    # Is this a threaded comment?
    if request.POST.get('parent_id'):
        comment.parent = Comment.objects.get(id=request.POST.get('parent_id'))

    # If commenter is logged in, override name and email with stored values from User object
    if request.user.is_authenticated:
        comment.name = request.user.get_full_name()
        comment.email = request.user.email

    # Set required relationship to Post object
    comment.post = post

    # Get commenter's IP and User-Agent string
    ip = get_ip(request)
    if ip is not None:
        comment.ip_address = ip
    comment.user_agent = request.META.get('HTTP_USER_AGENT', '')

    # Run spam check
    comment.spam = spam_check(comment)

    # Strip disallowed HTML tags. See tangerine docs to customize.
    comment.body = sanitize_comment(comment.body)

    # Call comment approval workflow
    comment.approved = get_comment_approval(comment.email, request.user.is_authenticated)
    if comment.approved:
        messages.add_message(request, messages.SUCCESS, 'Your comment has been posted.')
    else:
        messages.add_message(request, messages.INFO, 'Your comment has been held for moderation.')

    comment.save()

    # Alert post author that comment needs moderation, or that it's been auto-published:
    send_comment_moderation_email(comment)


def akismet_spam_ham(comment):
    """Submit comment to Akismet spam/ham API, using current spam status"""

    config = Blog.objects.first()
    if config.akismet_key:

        akismet_api = akismet.Akismet(key=config.akismet_key, blog_url=config.site_url)

        kwargs = {
            'comment_author': comment.name,
            'comment_author_email': comment.email,
            'comment_author_url': comment.website,
            'comment_content': comment.body
        }

        if comment.spam is True:
            submit = akismet_api.submit_spam(comment.ip_address, comment.user_agent, **kwargs)
        else:
            submit = akismet_api.submit_ham(comment.ip_address, comment.user_agent, **kwargs)

        return submit


def toggle_spam(comment):
    """Toggle spam status for a comment.

    Takes a comment, returns nothing.

    If input comment was not spam, toggle to ham, and vice versa.
    Make the assumption that spam should be unapproved, and ham approved, so also call toggle_approval().
    Also inform Akismet about spam status, if enabled.
    """

    # Submit to Akismet API, if enabled.
    akismet_spam_ham(comment)

    # Flip spam status to the opposite of whatever it is now, regardless whether Akismet is enabled.
    comment.spam = not comment.spam
    comment.save()
    toggle_approval(comment)


def spam_check(comment):
    # Pass comment object into configured spam control engines and return True or False
    config = Blog.objects.first()
    spam_status = False

    if config.akismet_key:
        akismet_api = akismet.Akismet(key=config.akismet_key, blog_url=config.site_url)
        spam_status = akismet_api.comment_check(
            comment.ip_address, comment.user_agent, comment_author=comment.name,
            comment_author_email=comment.email, comment_author_url=comment.website,
            comment_content=comment.body)

        return spam_status

    return spam_status


def get_search_qs(q):
    # Testable ORM query for returning search terms
    if q:
        qs = Post.objects.filter(
            Q(title__icontains=q) |
            Q(summary__icontains=q) |
            Q(content__icontains=q)
        )
    else:
        q = None
        qs = Post.objects.none()
    return qs
