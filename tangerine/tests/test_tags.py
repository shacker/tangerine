import pytest

from tangerine.templatetags.tangerine_tags import get_related_links, get_categories, get_settings
from tangerine.factories import RelatedLinkGroupFactory, CategoryFactory, ConfigFactory
from tangerine.models import Category


@pytest.mark.skip(reason="")
@pytest.mark.django_db
def test_get_settings():
    ConfigFactory()
    config = get_settings()
    assert len(config['site_title']) > 5
    assert len(config['tagline']) > 5
    assert len(config['num_posts_per_list_view']) > 1
    assert config['google_analytics_id'] != ''


@pytest.mark.django_db
def test_get_related_links_template_tag():
    rel = RelatedLinkGroupFactory()
    link_group = get_related_links(rel.slug)
    assert len(link_group['links']) == 5
    assert len(link_group['links'][0].site_title) > 1
    assert len(link_group['links'][0].site_url) > 1


@pytest.mark.django_db
def test_get_categories():
    num_cats = 10
    CategoryFactory.create_batch(num_cats)
    cats = get_categories()
    assert isinstance(cats, dict)
    assert len(cats.get('categories')) == num_cats
    # Ensure at least some of categories pulled from db are in the list returned by template tag
    assert Category.objects.first() in cats.get('categories')
    assert Category.objects.last() in cats.get('categories')
