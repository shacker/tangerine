# Tangerine

## Super-clean, pluggable Django blogging engine

*Just the bits you need, nothing more.*

Tangerine is a pluggable blogging system for Django, meant to be dropped into an *existing Django project*. Of course, nothing prevents you from running Tangerine as a standalone blog - you'll just need to create a basic/starter Django project first (if you need a starter site, check out the companion [Tangelo](https://github.com/shacker/tangelo) project, which supports the author's own Tangerine blog).

**Supports:**

- Post lists/detail/permalink views
- Page views for semi-static pages ("About", etc.)
- Tags and categories with views
- Spam-filtered commenting
- Author profiles
- Syntax highlighting for code samples
- "Trash" system
- List view pagination
- WordPress importer
- Blogroll (related link sets)
- OEmbed support
- Search
- Rich text editor
- Configurable via admin:
    - Site title
    - Num posts per list view

NOT intended to be "just like WordPress," but rather "an ideal blog engine for Django devs with some lessons learned from WordPress."

**Assumes:**

- Python 3.5+
- Django 2.0+ *

* Tangerine uses the new `path`-style routes in Django 2, not the older `url`-style routes.

### Installation

1. Create a running "container" site with working logins
1. Add `'tangerine',` to your `INSTALLED_APPS`
1. Set your timezone in settings, e.g. `TIME_ZONE = 'America/Los_Angeles'`
1. `./manage.py migrate`
1. Create starter posts, categories, blogroll, and a user for yourself (don't skip this!):
`./manage.py tangerine_start`

### Requirements and Recommendations for Container Site

For full/best functionality, we recommend adding these tags to the base template in your container site:

```
{% block tangerine_extra_head %}{% endblock tangerine_extra_head %} {# In HTML head #}
{% block tangerine_extra_css %}{% endblock tangerine_extra_css %}  {# In HTML head #}
{% block tangerine_extra_js %}{% endblock tangerine_extra_js %}  {# Before end of html body #}
```

Include meta-description and author tags, syntax highlighter CSS, JS ^

favicon.ico [how-to]

We intentionally don't provide a Theme system for Tangerine - you can style your site with any HTML/CSS templates you find in the wild, or create your own. Use the provided `templates` directory as a starting point [how-to here]. We assume your base template is called `base.html` and we extend that. Replace this in Tangerine templates if you use some other filename.

### Posts vs Pages

Similar to WordPress: New entries default to ptype "Post", but can be toggled to "Page." Posts are timestamped and shown in a list, sorted by date. Post detail views include the date in the URL.

In contrast, Pages are excluded from list views and are accessible at `/foo` where `foo` = the slug of the entry. Pages are intended for placement in menus and would include things like "About" or "Contact" pages.

The Django Admin includes a list filter to let you quickly sort Posts vs. Pages.

Quick start
-----------

1. Add to your INSTALLED_APPS:

```
INSTALLED_APPS = [
    ...
    'tangerine',
]
```

2. Include tangerine's URLconf in your project `urls.py`:

`url(r'^blog/', include('tangerine.urls')),`

3. Run `python manage.py migrate` to create the tangerine models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a post.

5. Visit http://127.0.0.1:8000

To run Tangerine's tests, add pytest to your virtualenv:
`pip install pytest` or `pipenv install pytest`
Then just run `pytest` from the projcect root.


## Templates

The provided template examples are meant to represent "reasonable defaults" and to show most possible templatetag usages. By all means, rearrange and season to taste (copy templates dir into your project's templates dir and tweak).

### Required in container site templates

Your `base.html` template must include:

`{% block content %}{% endblock content %}``

### Categories

Define them in Admin, make sure your base template includes a block:

`{% block categories %}{% endblock categories %}`

and display them with e.g.:

```
{% load tangerine_tags %}
...
{% block categories %}
    {% get_categories as cats %}
    {% if cats %}
        <h3>Categories</h3>
        <ul>
            {% for cat in cats.categories %}
                <li><a href="{% url 'tangerine:category' cat.slug %}">{{ cat.title }}</a></li>
            {% endfor %}
        </ul>
    {% endif %}
{% endblock categories %}
```

(included in default templates).


### RelatedLinkGroups

Tangerine supports multiple `RelatedLinkGroup`s, which are named collections of related links (such as a blogroll). A default `blogroll` set is provided in the `tangerine_start` command and referenced in the sample templates. You can either edit that set in the Admin (Posts/Related Link Groups) or create new ones and reference them from templates:

```
{% load tangerine_tags %}
...
{% block blogroll %}
    {% get_related_links 'blogroll' as link_group %}
    {% if link_group %}
        <h3>Blogroll</h3>
        <ul>
        {% for link in link_group.links %}
            <li><a href="{{ link.site_url }}">{{ link.site_title }}</a></li>
        {% endfor %}
        </ul>
    {% endif %}
{% endblock blogroll %}
```

### Internal links

To link to any internal Post or Page, do this in a template:

    `<a href="{% url 'post_detail' 'about' %}">About</a>`

where `'about'` is replaced with the slug of the page or post .

n.b. A starter About page should already exist in your initial data load.

### Title tags

Tangerine supplies content for the HTML `title` tag in:

`{% block title %}...{% endblock title %}`

If you have a `block title` in your base.html, it should be populated automatically. If you use another block name, you'll need to change what's being sent from the tangerine templates.

## Running tests
# export DJANGO_SETTINGS_MODULE=config.test
ln -s /Users/shacker/dev/tangerine .  # Do it with a symlink, not a pip install!
pipenv run pytest 
