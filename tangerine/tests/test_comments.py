import pytest

from tangerine.factories import PostFactory, CommentFactory, ConfigFactory
from tangerine.models import Comment, ApprovedCommentor
from tangerine.utils import sanitize_comment, get_comment_approval


@pytest.fixture()
def cats_and_posts():
    PostFactory.create_batch(30)


@pytest.mark.django_db
def test_unapproved_comments_not_in_qs():
    # Tests CommentManager
    post = PostFactory()
    CommentFactory.create_batch(5, post=post)
    CommentFactory.create_batch(3, post=post, approved=False)
    assert Comment.objects.all().count() == 8
    assert Comment.pub.all().count() == 5


@pytest.mark.django_db
def test_comment_approval():
    # Second arg to get_comment_approval() is a bool: whether they're authenticated or not.
    config = ConfigFactory()

    # Comments from authenticated users should always be approved.
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
def test_threaded_comments():
    # Methods on Post and Comment let us get all top-level comments for a Post,
    # and get child comments of a comment. Create 5 top-level comments, then 3 child comments
    # of the last comment. Check numbers.

    p = PostFactory()
    CommentFactory.create_batch(5, post=p)
    assert p.top_level_comments().count() == 5

    last_comment = p.top_level_comments().last()
    CommentFactory.create_batch(3, post=p, parent=last_comment)
    assert last_comment.child_comments().count() == 3

    # Now check again - count of top-level should still be 5, even though we've added more comments to the Post.
    assert p.top_level_comments().count() == 5

    # Tests for posting of child comments is in test_views, since comment threaded is initiated/handled in templates.


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
