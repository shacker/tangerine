import pytest

from tangerine.factories import CategoryFactory, PostFactory


@pytest.mark.django_db
def test_post_in_multiple_cats():
    cat1 = CategoryFactory(title="Foo")
    cat2 = CategoryFactory(title="Bar")
    post = PostFactory()
    post.categories.add(cat1)
    post.categories.add(cat2)
    assert post.categories.all().count() == 2
