import pytest

from tangerine.templatetags.tangerine_tags import get_related_links, get_categories
from tangerine.factories import RelatedLinkGroupFactory, CategoryFactory
from tangerine.models import Category


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
