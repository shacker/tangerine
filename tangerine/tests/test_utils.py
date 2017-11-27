import pytest

from tangerine.factories import PostFactory, CommentFactory, ConfigFactory
from tangerine.models import ApprovedCommentor
from tangerine.utils import sanitize_comment, get_comment_approval, toggle_approval


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
