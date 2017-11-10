import pytest

from tangerine.factories import PostFactory
from tangerine.models import Post


@pytest.mark.django_db
def test_post_factory():
    post = PostFactory()
    assert isinstance(post, Post)
    assert len(post.about) > 5
