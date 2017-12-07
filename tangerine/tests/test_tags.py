import pytest

from tangerine.templatetags.tangerine_tags import (
    get_related_links, get_categories, get_settings, gravatar, get_recent_comments)
from tangerine.factories import (
    RelatedLinkGroupFactory, CategoryFactory, ConfigFactory, PostFactory, CommentFactory)
from tangerine.models import Category, Post, Comment


@pytest.mark.django_db
def test_get_settings():
    ConfigFactory()
    config = get_settings()
    assert len(config['site_title']) > 5
    assert len(config['tagline']) > 5
    assert config['num_posts_per_list_view'] > 1


@pytest.mark.django_db
def test_get_related_links_template_tag():
    rel = RelatedLinkGroupFactory()
    link_group = get_related_links(rel.slug)
    assert len(link_group['links']) == 5
    assert len(link_group['links'][0].site_title) > 1
    assert len(link_group['links'][0].site_url) > 1


@pytest.mark.django_db
def test_get_non_empty_categories():
    # Don't show empty categories in template tag. It's OK for cats with unpublished or trashed posts
    # to be returned, unless they are the *only* post in the category.

    # Create good categories with published posts
    num_cats = 5
    CategoryFactory.create_batch(num_cats)
    for c in Category.objects.all():
        p = PostFactory(published=True, trashed=False)
        p.categories.add(c)

    # Make categories with both published/unpublished and trashed/untrashed posts
    has_trashed_cat = CategoryFactory()
    trashed_post = PostFactory(trashed=True)
    non_trashed_post = PostFactory(trashed=False)
    trashed_post.categories.add(has_trashed_cat)
    non_trashed_post.categories.add(has_trashed_cat)

    has_unpub_cat = CategoryFactory()
    unpub_post = PostFactory(published=False)
    pub_post = PostFactory(published=True)
    unpub_post.categories.add(has_unpub_cat)
    pub_post.categories.add(has_unpub_cat)

    empty_cat = CategoryFactory()

    # Number of cats found by template tag should now be 7 since these cats have both published and untrashed posts.
    cats = get_categories()
    assert isinstance(cats, dict)
    assert len(cats.get('categories')) == 7

    # Create cats with *only* unpub or trashed posts
    has_only_trashed_cat = CategoryFactory()
    trashed_post = PostFactory(trashed=True)
    trashed_post.categories.add(has_only_trashed_cat)

    has_only_unpub_cat = CategoryFactory()
    unpub_post = PostFactory(published=False)
    unpub_post.categories.add(has_only_unpub_cat)

    # Number of cats found by template tag should *still* be 7
    cats = get_categories()
    assert len(cats.get('categories')) == 7

    # Final reckoning
    goodcats = cats.get('categories')
    assert has_trashed_cat in goodcats
    assert has_unpub_cat in goodcats
    assert has_only_trashed_cat not in goodcats
    assert has_only_unpub_cat not in goodcats
    assert empty_cat not in goodcats


@pytest.mark.django_db
def test_get_recent_comments():
    PostFactory.create_batch(10, published=True)
    for post in Post.objects.all():
        CommentFactory.create_batch(3, post=post)

    # Generate 30 comments in system, but request back only n through the template tag.
    recent = get_recent_comments(10)
    assert len(recent['comments']) == 10
    recent = get_recent_comments(7)
    assert len(recent['comments']) == 7

    # Check object type of first element in return list
    assert isinstance(recent['comments'][0], Comment)


def test_gravatar_tag():
    img_url = gravatar('you@example.com')
    assert img_url.startswith('http://www.gravatar.com/avatar/')
    assert 'size=40' in img_url

    img_url = gravatar('you@example.com', size=60)
    assert 'size=60' in img_url
