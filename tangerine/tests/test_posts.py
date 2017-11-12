import pytest

from tangerine.factories import CategoryFactory, PostFactory
from tangerine.models import Post


@pytest.mark.django_db
def test_post_factory():
    CategoryFactory.create_batch(5)
    post = PostFactory()
    assert isinstance(post, Post)
    assert len(post.content) > 5
