from django import template

from tangerine.models import RelatedLinkGroup

register = template.Library()


@register.simple_tag
def get_related_links(slug):
    '''
    You can create as many Related Link Groups as you like (e.g. "Blogroll"), and order the
    links they contain in the admin by dragging and dropping.

    This template tag returns the set of *ordered* links in the named group as a list:

    {'links': related_links}

    To use in a template:

    {% load tangerine_tags %}
    {% get_related_links 'blogroll' as link_group %}
    {% for link in link_group.links %}
        <li><a href="{{ link.site_url }}">{{ link.site_title }}</a></li>
    {% endfor %}
    '''

    group = RelatedLinkGroup.objects.get(slug=slug)

    return {
        'links': group.relatedlink_set.all(),
    }
