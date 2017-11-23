import pytest

from tangerine.factories import PostFactory, CommentFactory
from tangerine.models import Comment


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
