import pytest

from django.conf import settings
from django.core import mail
from django.shortcuts import reverse

from tangerine.factories import PostFactory, CommentFactory, ConfigFactory
from tangerine.models import ApprovedCommentor
from tangerine.utils import (
    sanitize_comment, get_comment_approval, toggle_approval,
    spam_check, akismet_spam_ham, send_comment_moderation_email
    )


@pytest.fixture(autouse=True)
# Set up an in-memory mail server to receive test emails
def email_backend_setup(settings):
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'


@pytest.mark.django_db
def test_comment_approval():
    config = ConfigFactory()

    # Comments from authenticated users should always be approved.
    # auto_approve_previous_commentors in settings defaults to True.
    # Second arg to get_comment_approval() is a bool: whether they're authenticated or not.
    assert get_comment_approval('joe@example.com', True) is True

    # Comments from unauthenticated users should be approved IF they are in the ApprovedCommentor table
    # and auto_approve_previous_commentors is True in settings.
    assert get_comment_approval('joe@example.com', False) is False

    ApprovedCommentor.objects.create(email='joe@example.com')
    assert get_comment_approval('joe@example.com', False) is True

    # Now change the config preference and try an email that IS stored in the table. Should now NOT be approved.
    config.auto_approve_previous_commentors = False
    config.save()
    assert get_comment_approval('joe@example.com', False) is False


@pytest.mark.django_db
def test_approval_toggle():
    config = ConfigFactory()  # auto_approve defaults to True
    post = PostFactory()

    c1 = CommentFactory(post=post, approved=False)
    assert not c1.approved
    assert not ApprovedCommentor.objects.filter(email=c1.email).exists()
    toggle_approval(c1)
    assert c1.approved
    assert ApprovedCommentor.objects.filter(email=c1.email).exists()

    # With auto_approve disabled, state is toggled but commenter is never in ApprovedCommentors
    config.auto_approve_previous_commentors = False
    config.save()

    c2 = CommentFactory(post=post, approved=False)
    assert not c2.approved
    assert not ApprovedCommentor.objects.filter(email=c2.email).exists()
    toggle_approval(c2)
    assert c2.approved
    assert not ApprovedCommentor.objects.filter(email=c2.email).exists()


def test_comment_sanitizer():
    # Not much to test here - bleach dependency is already heavily tested.
    # Just ensure that our util function is alive and kicking.

    # No HTML
    comment = 'This is a test'
    assert sanitize_comment(comment) == comment

    # Allowed HTML
    comment = 'This <b>is</b> a test'
    assert sanitize_comment(comment) == comment

    # Disallowed HTML
    comment = 'This <script>is</script> a test'
    assert sanitize_comment(comment) == 'This is a test'


@pytest.mark.django_db
def test_spam_check():
    """For now we are just testing our route to the Akismet API and whether we store submitted comments
    as spam or not. Later expand this into multiple tests to support multiple spam checking engines.

    Devs who want to run this test *must* add to their *test* settings:
    AKISMET_KEY = 'abc123' and SITE_URL = 'https://your.registered.domain'
    (but with real values). Otherwise we can't run tests that call their API with YOUR credentials.
    See https://akismet.com/development/api/#detailed-docs for notes on testing Akismet API calls."""

    if hasattr(settings, 'AKISMET_KEY'):

        ConfigFactory(akismet_key=settings.AKISMET_KEY, site_url=settings.SITE_URL)
        post = PostFactory()

        # Good comment:
        c1 = CommentFactory(post=post, email='akismet-guaranteed-spam@example.com')
        c2 = CommentFactory(post=post)

        assert spam_check(c1) is True
        assert spam_check(c2) is False


@pytest.mark.django_db
def test_submit_aksimet_spam():
    """Akismet API will believe what we tell it (return True if we say it's spam and vice versa). So simple check."""

    if hasattr(settings, 'AKISMET_KEY'):

        ConfigFactory(akismet_key=settings.AKISMET_KEY, site_url=settings.SITE_URL)
        post = PostFactory()

        c1 = CommentFactory(post=post, email='akismet-guaranteed-spam@example.com', spam=True)

        assert akismet_spam_ham(c1) is True


@pytest.mark.django_db
def test_send_comment_moderation_email(email_backend_setup, admin_user):
    """Email should be sent with a different subject and body depending on whether it needs moderation."""

    site_title = "foobar blog"
    site_url = "http://example.com"
    comment_body = "hello world"
    from_email = "you@example.com"
    moderation_email = "another@example.com"

    ConfigFactory(site_url=site_url, site_title=site_title, from_email=from_email, moderation_email=moderation_email)
    post = PostFactory(author=admin_user)

    # Test spam first
    comment = CommentFactory(body=comment_body, post=post, spam=True, approved=False)
    send_comment_moderation_email(comment)
    sent_msg = mail.outbox[0]
    path = reverse('tangerine:manage_comment', kwargs={'comment_id': comment.id})

    assert len(mail.outbox) == 1
    assert sent_msg.subject == "A new comment on {} requires moderation".format(site_title)
    assert comment_body in sent_msg.body  # Content is wrapped in email template, so not identical
    assert "{}{}".format(site_url, path) in sent_msg.body  # Email includes comment moderation link
    assert sent_msg.from_email == from_email
    assert moderation_email in sent_msg.recipients()

    # Then ham
    comment = CommentFactory(body=comment_body, post=post, spam=False, approved=True)
    send_comment_moderation_email(comment)
    sent_msg = mail.outbox[1]
    assert sent_msg.subject == "A new comment on {} has been automatically published".format(site_title)
