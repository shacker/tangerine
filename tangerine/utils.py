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
