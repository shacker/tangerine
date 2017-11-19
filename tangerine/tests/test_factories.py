import pytest
from datetime import datetime

from tangerine.factories import (
    CategoryFactory, PostFactory, RelatedLinkGroupFactory,
    RelatedLinkFactory, CommentFactory)
from tangerine.models import Post, Category, RelatedLinkGroup, RelatedLink, Comment


@pytest.fixture()
def make_cats():
    CategoryFactory.create_batch(10)


@pytest.mark.django_db
def test_post_factory(make_cats):
    post = PostFactory(title="Space and Drums")
    assert isinstance(post, Post)
    assert len(post.content) > 5
    assert len(post.summary) > 5
    assert post.slug == 'space-and-drums'
    assert isinstance(post.created, datetime)


@pytest.mark.django_db
def test_category_factory():
    cat = CategoryFactory.create(title='Estimated Prophet')
    assert isinstance(cat, Category)
    assert cat.slug == 'estimated-prophet'


@pytest.mark.django_db
def test_related_link_group_factory():
    rel = RelatedLinkGroupFactory.create(slug='foobar')
    assert isinstance(rel, RelatedLinkGroup)
    assert rel.relatedlink_set.all().count() == 5


@pytest.mark.django_db
def test_related_link_factory():
    g = RelatedLinkGroupFactory()
    link = RelatedLinkFactory.create(group=g)
    assert isinstance(link, RelatedLink)
    assert len(link.site_title) > 3
    assert link.site_url.startswith('http')


@pytest.mark.django_db
def test_comment_factory():
    p = PostFactory()
    comment = CommentFactory.create(post=p)
    assert isinstance(comment, Comment)
    assert len(comment.name) > 3
    assert comment.website.startswith('http')
    assert '@' in comment.email
