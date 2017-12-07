from libgravatar import Gravatar

from django import template

from tangerine.models import Category, RelatedLinkGroup, Config, Comment

register = template.Library()


@register.simple_tag
def get_settings():
    '''
    There is one and only one Config record in the Admin, which contains the Site Title, Tagline,
    Google Analytics ID and number of posts per page. Get this once in the base template to provide
    settings options in a dictionary to all tangerine pages.

    To use in a template block:

    {% load tangerine_tags %}
    {% get_settings as tangerine %}
    ...
    {# then any of these *inside* the block tag that needs them: #}
    {{ tangerine.site_title }}
    {{ tangerine.tagline }}
    {{ tangerine.num_posts_per_list_view }}
    {{ tangerine.google_analytics_id }}
    {{ tangerine.enable_comments_global }}
    {{ tangerine.comment_system }}
    '''

    try:
        config = Config.objects.all().first()
        return {
            'site_title': config.site_title,
            'tagline': config.tagline,
            'num_posts_per_list_view': config.num_posts_per_list_view,
            'enable_comments_global': config.enable_comments_global,
            'comment_system': config.comment_system,
        }
    except AttributeError:
        raise AttributeError("Site not yet configured. Visit Tangerine/Config in the Admin and create a Config record.")


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
    '''Returns the set of all categories *with published posts* as an ordered list of Category objects.

    {'categories': categories}

    To use in a template:

    {% load tangerine_tags %}
    ...
    {% get_categories as cats %}
    {% for cat in cats.categories %}
        <li><a href="{% url 'category' cat.slug %}">{{ cat.name }}</a></li>
    {% endfor %}
    '''
    cats = []
    for c in Category.objects.all():
        if c.post_set.filter(trashed=False, published=True).count() > 0:
            cats.append(c)

    return {
        'categories': cats,
    }


@register.simple_tag
def get_recent_comments(num_comments=10):
    '''Returns n most-recent published comments as a list.

    To use in a template:

    {% load tangerine_tags %}
    ...
    {# Replace 10 with desired number of comments #}
    {% get_recent_comments 10 as recent_comments %}
    {% if recent_comments %}
        <h3>Recent Comments</h3>
        <ul class="recent_comments">
            {% for comment in recent_comments.comments %}
                <li><a href="{{ comment.post.get_absolute_url }}#comment-{{ comment.id }}">{{ comment.name}}</a>,
                    {{ comment.created|date:"SHORT_DATE_FORMAT" }}<br />
                    {{ comment.body|striptags|truncatechars:25}}</li>
            {% endfor %}
        </ul>
    {% endif %}
    '''

    # Return approved comments only
    return {
        'comments': Comment.pub.order_by('-created')[:num_comments],
    }


@register.filter
def gravatar(email, size=40):
    '''Get commenter's avatar from Gravatar service via API (depends on libgravatar)'''
    g = Gravatar(email)
    return g.get_image(size, "mm")
