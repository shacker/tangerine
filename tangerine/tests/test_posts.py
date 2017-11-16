import pytest

from tangerine.factories import CategoryFactory, PostFactory, RelatedLinkGroupFactory
from tangerine.models import RelatedLinkGroup, Post


@pytest.fixture()
def cats_and_posts():
    CategoryFactory.create_batch(10)
    PostFactory.create_batch(30)


@pytest.mark.django_db
def test_post_in_multiple_cats():
    cat1 = CategoryFactory(title="Foo")
    cat2 = CategoryFactory(title="Bar")
    post = PostFactory()
    post.categories.add(cat1)
    post.categories.add(cat2)
    assert post.categories.all().count() == 2


@pytest.mark.django_db
def test_unique_blogroll():
    # We can create multiple blogrolls with same slug, but they are overidden each time, so we should end up with 1
    RelatedLinkGroupFactory.create_batch(5, slug='foo')
    assert RelatedLinkGroup.objects.filter(slug='foo').count() == 1


@pytest.mark.django_db
def test_unpublished_post_not_in_qs(cats_and_posts):
    somepost = PostFactory(published=False)
    qs = Post.pub.all()
    assert somepost not in qs


@pytest.mark.django_db
def test_trashed_post_not_in_qs(cats_and_posts):
    somepost = PostFactory(trashed=True)
    qs = Post.pub.all()
    assert somepost not in qs
