import akismet
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


def akismet_spam_ham(comment):
    """Submit comment to Akismet spam/ham API, using current spam status"""

    config = Config.objects.first()
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
    config = Config.objects.first()
    spam_status = False

    if config.akismet_key:
        akismet_api = akismet.Akismet(key=config.akismet_key, blog_url=config.site_url)
        spam_status = akismet_api.comment_check(
            comment.ip_address, comment.user_agent, comment_author=comment.name,
            comment_author_email=comment.email, comment_author_url=comment.website,
            comment_content=comment.body)

        return spam_status

    return spam_status
