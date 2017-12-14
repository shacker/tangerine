# Tangerine

## Super-clean, pluggable Django blogging engine

*Just the bits you need, nothing more.*

Tangerine is a pluggable blogging system for Django, meant to be dropped into an *existing Django project*. Of course, nothing prevents you from running Tangerine as a standalone blog - you'll just need to create a basic/starter Django project first (if you need a starter site, check out the companion [Tangelo](https://github.com/shacker/tangelo) project, which supports the author's own Tangerine blog).

**Supports:**

- Post lists/detail/permalink views
- Page views for semi-static pages ("About", etc.)
- Tags and categories with views
- Author profiles (no)
- Syntax highlighting for code samples
- "Trash" system
- Pagination
- WordPress importer
- Native *threaded* commenting system with spam control
- Support for Disqus and Facebook comments coming soon
- Gravatar support in comments
- Blogroll (related link sets)
- Google Analytics integration
- Comment moderation (list and detail), with email notifications
- Integrated Akismet spam control
- Mark comments spam/ham, or approved/unapproved
- OEmbed support
- Search (posts and comments)
- Rich text editor
- Configurable via admin:
    - Site title
    - Num posts per list view

NOT intended to be "just like WordPress," but rather "an ideal blog engine for Django devs with some lessons learned from WordPress."

**Assumes:**

- Python 3.5+
- Django 2.0+

Tangerine uses the new `path`-style routes in Django 2, not the older `url`-style routes, so Django 2+ really is a requirement.



## Quick start

1. Create a running "container" site with working logins.

1. Add `'tangerine',` to your `INSTALLED_APPS`:

	```
	INSTALLED_APPS = [
	    ...
	    'tangerine',
	]
	```

1. Set your timezone in settings, e.g. `TIME_ZONE = 'America/Los_Angeles'`

1. Include tangerine's URLconf in your project `urls.py`:

	`url(r'^blog/', include('tangerine.urls')),`

1. Run `python manage.py migrate` to create the tangerine models.

1. Create starter content and a superuser for yourself (don't skip this!): Run `python manage.py tangerine_start` to perform installation tasks and set up dummy data and config.


1. Start the development server and visit http://localhost:8000/admin/
   to create a post. 
   
1. While you're in the admin, go to Tangerine/Config to set your site title, optional Google Analytics ID, and other configuration options.

1. Delete the starter content via Admin or from Django shell.

1. Optionally import existing content from WordPress export file (see below)



## Configuration

Tangerine configuration settings are made in the Django Admin, not in your project settings. If you ran the `tangerine_start` script, default settings will have been created for you, but you'll still want to visit Admin|Tangerine|Config to tweak them. All of the Config settings should be fairly self-explanatory (see the help_text on each field).

Tangerine will crash if you have not created a Config record!


## Requirements for Container Site

Tangerine is a *pluggable* app, not a full web application. We assume you already have a working Django site into which you are installing Tangerine. 

For full/best functionality, add these tags to the base template in your container site:

```
{% block tangerine_extra_head %}{% endblock tangerine_extra_head %}  # In HTML head
{% block tangerine_extra_css %}{% endblock tangerine_extra_css %}   # In HTML head
{% block footer %}{% endblock footer %}  # Before end of html body
{% block tangerine_extra_js %}{% endblock tangerine_extra_js %}  # Before end of html body

{% block sidebar %}{% endblock sidebar %}

```



Include meta-description and author tags, syntax highlighter CSS, JS ^





We intentionally don't provide a Theme system for Tangerine - you can style your site with any HTML/CSS templates you find in the wild, or create your own. Use the provided `templates` directory as a starting point [how-to here]. We assume your base template is called `base.html` and we extend that. Replace this in Tangerine templates if you use some other filename.

### Posts vs Pages

Similar to WordPress: New entries default to ptype "Post", but can be toggled to "Page." Posts are timestamped and shown in a list, sorted by date. Post detail views include the date in the URL.

In contrast, Pages are excluded from list views and are accessible at `/foo` where `foo` = the slug of the entry. Pages are intended for placement in menus and would include things like "About" or "Contact" pages.

The Django Admin includes a list filter to let you quickly sort Posts vs. Pages.



## Commenting
Native vs. Disqus, Google, etc.

## Templates

The provided template examples are meant to represent "reasonable defaults" and to show most possible templatetag usages. By all means, rearrange and season to taste (copy templates dir into your project's templates dir and tweak).

### Required in container site templates

Your `base.html` template must include:

`{% block content %}{% endblock content %}`

Global tangerine settings set in the admin via Tangerine/Config (site title, tagline, posts per page, google analytics, etc.) can be accessed in templates like this:

```
{# Near top of file: #}
{% load tangerine_tags %}

{# Inside the block that needs it: #}
{% block content %}
    {% get_settings as tangerine %}
    <h1 class="site_title">{{ tangerine.site_title }}</h1>
    ...
{% endblock content %}
```

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

[Check this]

To link to any internal Post or Page, do this in a template:

`<a href="{% url 'post_detail' 'about' %}">About</a>`

where `'about'` is replaced with the slug of the page or post .

n.b. A starter About page should already exist in your initial data load.

### Title tags

Tangerine supplies content for the HTML `title` tag in:

`{% block title %}...{% endblock title %}`

If you have a `block title` in your base.html, it should be populated automatically. If you use another block name, you'll need to change what's being sent from the tangerine templates.

## Running tests

Tangerine includes a very complete test suite, which will always pass before new versions are released. There is little reason for end users to run Tangerine tests, but if you want to, do:

```
export DJANGO_SETTINGS_MODULE=config.test
ln -s /Users/shacker/dev/tangerine .  # Do it with a symlink, not a pip install!
pipenv run pytest 
```

### Gravatar

Gravatar support in comment templates is present by default, and avatars are derived from the commenter's email, if they have a gravatar account:

`<img src="{{ comment.email|gravatar:60 }}" alt="" />`

The fallback icon is the class "Mystery Man" ("mm"). This can be changed to one of the [other defaults](https://en.gravatar.com/site/implement/images/) by changing the template tag itself (room for improvement there).

### Sanitizing Comments

Malicious HTML will be stripped from posted comments via `bleach`. The default set of allowed tags is:

`['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'strong', 'ul']`

To override, add to your project settings e.g.:

`BLEACH_ALLOWED_TAGS = ['hr', 'b', 'i']`


### Extra JS

`{% block extra_js %}{% endblock extra_js %}`

We assume you have jquery installed!

### Comment Moderation

View is at ...

By default, the emails of approved comments are added to an ApprovedCommentors table, and future comments from those email addresses will be auto-approved. To disable this setting, turn it off in the Admin config.

## Adding Functionality

Tangerine does not (yet?) provide "plugin" capability like WordPress because we feel that most new functionality can be provided as a template tag created in your own app. Please see the template tags provided by Tangerine as examples, then create your customizations in your own app or project and load them into your template customizations. If you think others would benefit from the same functionality, make a pull request!

Functionality that cannot be provided by template tags should be submitted as a pull request to Tangerine. 

-----------

### Akismet Spam Checking

Because WordPress runs 20% of the internet, and Akismet is bundled with every WordPress installation, millions of users are constantly submitting spam and ham feedback to the Akismet service. Akismet is *incredibly* effective at spam control. Fortunatley, Akismet isn't tied to WordPress - it's available to anyone, and excellent Python libs exist for communicating with its API.

Tangerine includes native Akismet support. [Get a key](https://akismet.com/) (free or paid), add it to your Tangerine config, and enjoy virtually automatic spam control. In Tangerine's Comment Moderation interface, use the Spam/Ham buttons to help train Aksimet for the benefit of others.

n.b.: Marking a comment as spam/ham also toggles its Approved/Unapproved status. But toggling the approval status does *not* affect the spam status of the comment (because you might have good reasons to unapprove a comment on your site other than it being spam, or you might want to approve a comment that Akismet thinks is spam for some reason).

Devs who want to run the spam_checks pytest *must* add to their `test.py` settings:
AKISMET_KEY = 'abc123' and SITE_URL = 'https://your.registered.domain' (but with real values). Otherwise we can't run tests that call their API with YOUR credentials.

-------

Tangerine divides into two spaces: The "management" interface for writing posts and comment moderation, and the appearance of your site within the project you've added it to. The public interface is controlled by the theme you choose and the customizations you've made to it, while the appearance of the Tangering "management" interface is not intended to be customized (though advanced users are free to override of course).

------

## Recent Comments

Add to your base.html:

```
{% block recent_comments %}{% endblock recent_comments %}

```

Then call the `recent_comments` template tag from the template where you want recent comments to appear, with the number of comments you want to display:

```
{% get_recent_comments 10 as recent_comments %}
{# Now loop through recent_comments.comments #}

```

See `home.html` in the default theme for a usage example.



-------

### Static files

Tangerine includes some CSS and Javascript for use in the management interface. To have Tangerine's static dir included in your project, add it to your project's `STATICFILES_DIRS `:

```
STATICFILES_DIRS = [
	...
    'tangerine/static'
]
```


### Running Tests

To run Tangerine's tests, add pytest to your virtualenv:
`pip install pytest` or `pipenv install pytest`
Then just run `pytest` from the projcect root.
