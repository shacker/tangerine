from django import template

from tangerine.models import Category, RelatedLinkGroup, Config

register = template.Library()


@register.simple_tag
def get_settings():
    '''
    There is one and only one Config record in the Admin, which contains the Site Title, Tagline,
    Google Analytics ID and number of posts per page. Get this once in the base template to provide
    settings options in a dictionary to all tangerine pages.

    To use in a template (really should just be tangerine/base.html but could be anywhere):

    {% load tangerine_tags %}
    {% get_settings as tangerine %}
    ...
    {# then any of these *inside* the block tag that needs them: #}
    {{ tangerine.site_title }}
    {{ tangerine.tagline }}
    {{ tangerine.num_posts_per_list_view }}
    {{ tangerine.google_analytics_id }}
    '''

    try:
        config = Config.objects.all().first()
        return {
            'site_title': config.site_title,
            'tagline': config.tagline,
            'num_posts_per_list_view': config.num_posts_per_list_view,
            'google_analytics_id': config.google_analytics_id,
        }
    except Config.DoesNotExist:
        return {}


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

    try:
        group = RelatedLinkGroup.objects.get(slug=slug)
        return {
            'links': group.relatedlink_set.all(),
        }
    except RelatedLinkGroup.DoesNotExist:
        return {
            'links': [
                {'site_title': 'Template tag asked for RelatedLinkGroup "{}" which does not exist in admin.'.format(
                    slug)}
                ],
        }


@register.simple_tag
def get_categories():
    '''Returns the set of all categories as an ordered list of Category objects.

    This template tag returns the set of *ordered* links in the named group as a list:

    {'categories': categories}

    To use in a template:

    {% load tangerine_tags %}
    ...
    {% get_categories as cats %}
    {% for cat in cats.categories %}
        <li><a href="{% url 'category' cat.slug %}">{{ cat.name }}</a></li>
    {% endfor %}
    '''

    return {
        'categories': Category.objects.all(),
    }
