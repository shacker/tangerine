import pytest

from tangerine.factories import CategoryFactory, PostFactory, RelatedLinkGroupFactory
from tangerine.models import RelatedLinkGroup


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
    # We can create multiple with same slug, but they are overidden each time, so we should end up with 1
    RelatedLinkGroupFactory.create_batch(5, slug='foo')
    assert RelatedLinkGroup.objects.filter(slug='foo').count() == 1
