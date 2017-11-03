# Tangerine

## Super-clean, pluggable Django blogging engine

*Just the bits you need, nothing more.*

**Supports:**

- Post lists/detail/permalink views
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
