from datetime import datetime

from libgravatar import Gravatar

from django import template
from django.utils.timezone import make_naive, make_aware, is_aware

from tangerine.models import Category, RelatedLinkGroup, Blog, Comment, Post

register = template.Library()


@register.simple_tag
def get_settings(blog_slug):
    """
    There is one Blog record in the Admin for each configured blog, which contains the Site Title, Tagline,
    Google Analytics ID and number of posts per page. Get this once in the base template to provide
    settings options in a dictionary to all tangerine pages.

    To use in a template block:

    {% load tangerine_tags %}
    {# blog_slug should be available automatically - passed in from URLs to each view #}
    {% get_settings as tangerine blog_slug %}
    ...
    {# then any of these *inside* the block tag that needs them: #}
    {{ tangerine.title }}
    {{ tangerine.slug }}
    {{ tangerine.tagline }}
    {{ tangerine.num_posts_per_list_view }}
    {{ tangerine.google_analytics_id }}
    {{ tangerine.enable_comments_global }}
    {{ tangerine.comment_system }}
    """

    try:
        config = Blog.objects.get(slug=blog_slug)
        return {
            "title": config.title,
            "slug": config.slug,
            "tagline": config.tagline,
            "num_posts_per_list_view": config.num_posts_per_list_view,
            "enable_comments_global": config.enable_comments_global,
            "comment_system": config.comment_system,
            "google_analytics_id": config.google_analytics_id,
        }
    except AttributeError:
        raise AttributeError(
            "Site not yet configured. Visit Tangerine/Config in the Admin and create a Config record."
        )


@register.simple_tag
def get_related_links(blog_slug):
    """
    Each blog or news site gets a RelatedLinkGroup ("blogroll") which can be displayed in the sidebar.

    This template tag returns the set of *ordered* links in the named group as a list:

    {'links': related_links}

    To use in a template:

    {% load tangerine_tags %}
    {% get_related_links blog_slug=blog_slug as link_group %}
    {% for link in link_group.links %}
        <li><a href="{{ link.site_url }}">{{ link.site_title }}</a></li>
    {% endfor %}
    """

    group = RelatedLinkGroup.objects.filter(blog__slug=blog_slug).first()
    if group:
        return {
            "links": group.relatedlink_set.all(),
        }
    else:
        return {
            "links": [{"site_title": "No RelatedLinkGroup found for this blog."}],
        }


@register.simple_tag
def get_date_archives(blog_slug, dtype="year", start="19700101", end="29991231"):
    """
    Args:
        dtype: One of 'year' or 'month', determining how "deep" returned dates should go
            (retrieve nested months?). Default: 'year'
        start: String in format yyyymmdd. No dates will be returned for posts earlier than this date.
        end: String in format yyyymmdd. No dates will be returned for posts later than this date.

    Returns:
        Queryset of qualifying datetime objects.

    `start` and `end` default to dates in the distant past and future (i.e. we default to "all dates").

    Returns a set of dates for which posts exist, to be parsed in the template with the `regroup` template tag.
    (We use `regroup` rather than fancy data structures to provide max customizability at the template level).
    """

    start = datetime.strptime(start, "%Y%m%d")
    end = datetime.strptime(end, "%Y%m%d")

    # To prevent TZ awareness from changing dates when they slip over the midnight boundary,
    # make dates TZ-naive if containing site uses TZ awareness (time=00:00:00).
    naive_start = make_naive(start) if is_aware(start) else start
    naive_end = make_naive(end) if is_aware(end) else end

    # Ironically, need to cast the naive dates back to `aware` to prevent console warnings,
    # since the ORM expects aware dates.
    qs = (
        Post.objects.dates("pub_date", dtype, "DESC")
        .filter(blog__slug=blog_slug)
        .exclude(pub_date__lt=make_aware(naive_start))
        .exclude(pub_date__gt=make_aware(naive_end))
    )
    return qs


@register.simple_tag
def get_categories(blog_slug):
    """Returns the set of all categories *with published posts* as an ordered list of Category objects.

    {'categories': categories}

    To use in a template:

    {% load tangerine_tags %}
    ...
    {% get_categories as cats blog_slug %}
    {% for cat in cats.categories %}
        <li><a href="{% url 'category' cat.slug %}">{{ cat.name }}</a></li>
    {% endfor %}
    """
    cats = []
    for c in Category.objects.filter(blog__slug=blog_slug):
        if c.post_set.filter(trashed=False, published=True).count() > 0:
            cats.append(c)

    return {
        "categories": cats,
    }


@register.simple_tag
def get_recent_comments(blog_slug, num_comments=10):
    """Returns n most-recent published comments as a list.

    To use in a template:

    {% load tangerine_tags %}
    ...
    {# Replace 10 with desired number of comments #}
    {% get_recent_comments blog_slug 10 as recent_comments %}
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
    """

    # Return approved comments only
    return {
        "comments": Comment.pub.filter(post__blog__slug=blog_slug).order_by("-created")[
            :num_comments
        ],
    }


@register.simple_tag
def get_all_blogs():
    """Returns all configured Blogs in the project as a queryset.

    To use in a template:

    {% load tangerine_tags %}
    ...
    {% get_all_blogs as blogs %}
    <h3>Blogs in This Project</h3>
    <ul class="blogs">
        {% for blog in blogs %}
            <li><a href="{% url 'tangerine:home' blog.slug %}">{{ blog.title }}</a></li>
        {% endfor %}
    </ul>
    """
    return Blog.objects.all()


@register.filter
def gravatar(email, size=40):
    """Get commenter's avatar from Gravatar service via API (depends on libgravatar)"""
    g = Gravatar(email)
    return g.get_image(size, "mm")
