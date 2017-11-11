# Tangerine

## Super-clean, pluggable Django blogging engine

*Just the bits you need, nothing more.*

**Supports:**

- Post lists/detail/permalink views
- Page detail for semi-static pages
- Tags and categories with views
- Spam-filtered commenting
- Author profiles
- Syntax highlighting for code samples
- "Trash" system
- List view pagination
- WordPress importer
- Blogroll
- OEmbed support
- Navigation system
- Search
- Rich text editor
- Configurable via admin:
    - Site title
    - Num posts per list view

NOT intended to be "just like WordPress," but rather "an ideal blog engine for Django devs."

**Assumes:**

- Python 3.5+
- Django 2.0+ *

* Tangerine uses the new `path`-style routes in Django 2, not the older `url`-style routes.

### Installation

- Create a running container site with working logins
- Add `'tangerine',` to your `INSTALLED_APPS`
- `./manage.py migrate`
- Create fake posts, categories, and a user for yourself: `./manage.py fake_posts` (see Initial Data, below)

Be sure to set your timezone in settings:

`TIME_ZONE = 'America/Los_Angeles'`

### Initial data

During development, you may want a bunch of Categories and Posts to work with so you know what things will look like.

After creating some categories manually, use this to create 500 faked posts for testing purposes:

`./manage.py fake_posts`


### Requirements and Recommendations for Container Site

Tangerine is a *pluggable* blog engine, intended to be dropped into an existing Django project. If you don't already have a running Django project, use the setup instructions above.

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

1. Add "polls" to your INSTALLED_APPS setting like this::

```
INSTALLED_APPS = [
    ...
    'django-tangerine',
]
```

2. Include the tangerine URLconf in your project urls.py like this::

`url(r'^blog/', include('tangerine.urls')),`

3. Run `python manage.py migrate` to create the tangerine models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a post (you'll need the Admin app enabled).

5. Visit http://127.0.0.1:8000/blog/ to participate in the poll.

If you want to run tests, add pytest to your virtualenv:
`pip install pytest` or `pipenv install pytest`
Then just run `pytest` from the projcect root.



------

TEMPLATES

Base template must include:
{% block content %}{% endblock content %}

If you want Related Links with a certain slug for the RelatedLinkGroup, use:
{% block blogroll %}{% endblock blogroll %}

Templates are meant to represent "reasonable defaults" and to show most possible templatetag usages. By all means, rearrange and season to taste. (copy templates dir into your project and tweak).

To link to a Page (rather than a post, do this in a template:
    
    <a href="{% url 'post_detail' 'about' %}">About</a>

