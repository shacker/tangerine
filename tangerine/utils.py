from akismet import Akismet
import bleach

from django.conf import settings

from tangerine.models import ApprovedCommentor, Config


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

    config = Config.objects.first()
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

    If auto_approve is enabled in config and comment is approved, also add user to ApprovedCommentors,
    (or remove if unapproving)."""

    config = Config.objects.first()
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


def spam_checks(comment):
    # Pass comment object into configured spam control engines and return True or False
    config = Config.objects.first()
    spam_status = False

    if config.akismet_key:
        akismet = Akismet(config.akismet_key, blog=config.site_url)
        spam_status = akismet.check(
            comment.ip_address, comment.user_agent, comment_author=comment.name,
            comment_author_email=comment.email, comment_author_url=comment.website,
            comment_content=comment.body)

        return spam_status

    # Add other spam control engines here.

    return spam_status
