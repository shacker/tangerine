# Tangerine

<img src="tangerine/static/tangerine/img/tangerine_logo.png" alt="Tangerine logo" style="width: 150px;"/>

## Super-clean, pluggable Django blogging engine

*Just the bits you need, nothing more.*

Tangerine is a *pluggable* blogging system for Django, meant to be dropped into an *existing Django project*. Of course, nothing prevents you from running Tangerine as a standalone blog - you'll just need to create a basic/starter Django project first (if you need a starter site, check out the companion [Tangelo](https://github.com/shacker/tangelo) project, which supports the author's own Tangerine blog).

Unlike other blogging systems for Django, Tangerine does not require you adopt someone else's complete content content management system, or to fundamentally alter basic Django practices and assumptions - Tangerine is a true "[reusable app](https://docs.djangoproject.com/en/2.0/intro/reusable-apps/)."

Tangerine is **not** intended to be "just like WordPress," but rather "an ideal blog engine for experienced Django devs, with some lessons learned from WordPress."

**Supports:**

- Standard blog Post pages
    - OEmbed support	
- Semi-static Pages (About, Contact, etc.)
- Multiple blogs in a single installation
- Tags and categories
- Date archives by year and month
- Pagination (customize number of posts per results page)
- Blogrolls (related link groups)
- Date archive link sets
- Tags and tag-specific views (`/foo/tags/python` lists all Python-related posts)
- RSS feeds (one per blog)
- Search (posts and comments)
- "Trash" system
- WordPress importer
- Google Analytics integration
- Feature-complete set of "fake" data for getting started/dev work (via FactoryBoy)
- Settings configurable via Django Admin:
    - Site title
    - Num posts per list view
    - More...
- Rich text editor
	- Syntax highlighting for code samples
- Commenting system
    - Gravatar support in comments
    - Support for Disqus and Facebook comments coming soon
    - Native *threaded* commenting system with spam control
    - Mark comments spam/ham, or approved/unapproved
    - Comment moderation (list and detail), with email notifications
    - Subscribe to comments (email notif when new comments added)
    - Integrated Akismet spam control
    - Recent Comments template tag


**Assumes:**

- Python 3.5+
- Django 2.0+

Tangerine uses the new `path`-style routes in Django 2, not the older `url`-style routes, so Django 2+ really is a requirement.

## Quick start

1. Create a running "container" site with working logins.

1. Add to your `INSTALLED_APPS`:

	```
	INSTALLED_APPS = [
	    ...
	    'tangerine',
	    'taggit',
	]
	```

1. Set your timezone in settings, e.g. `TIME_ZONE = 'America/Los_Angeles'`

1. Include tangerine's URLconf in your project `urls.py`:

    `path('<blog_slug>/', include('tangerine.urls', namespace='tangerine')),`

1. Run `python manage.py migrate` to create the tangerine models.

1. Create starter content and a superuser for yourself (don't skip this!): Run `python manage.py tangerine_start` to perform installation tasks and set up dummy data in example blogs (this step generates sample data with FactoryBoy).

1. Start the development server and visit [http://localhost:8000/admin/](http://localhost:8000/admin/)
   to create a post. 
   
1. While you're in the admin, go to Tangerine/Config to set your site title, optional Google Analytics ID, and other configuration options. If your site will have multiple blog instances, you'll need one Blog config record for each blog.

1. When you've got the hang of the system, delete or edit the starter content via Admin or from Django shell.

1. Optionally import existing content from WordPress export file (see below)

### Management Interface

Tangerine divides into two spaces: The "management" interface for writing posts and comment moderation, and the appearance of your site within the project you've added it to. The public interface is controlled by the theme you choose and the customizations you've made to it, while the appearance of the Tangering "management" interface is not intended to be customized (though advanced users are free to override of course).

## Configuration

Tangerine configuration settings are made in the Django Admin, not in your project settings. If you ran the `tangerine_start` script, default settings for dummy blogs will have been created for you, but you'll still want to visit Admin|Tangerine|Config to tweak them. All of the Config settings should be fairly self-explanatory (see the `help_text` on each field).

If you will be running multiple tangerine instances in your site, you'll need one Blog record in the Admin for each blog or news site.

Tangerine will do nothing if you do not have at least one Blog record!


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

Include meta-description and author tags, syntax highlighter CSS, JS

We intentionally don't provide a Theme system for Tangerine - you can style your site with any HTML/CSS templates you find in the wild, or create your own. Use the provided `templates` directory as a starting point [how-to here]. We assume your base template is called `base.html` and we extend that. Replace this in Tangerine templates if you use some other filename.

### Posts vs Pages

Similar to WordPress: New entries default to ptype "Post", but can be toggled to "Page." Posts are timestamped and shown in a list, sorted by date. Post detail views include the date in the URL.

In contrast, Pages are excluded from list views and are accessible at `/foo` where `foo` = the slug of the entry. Pages are intended for placement in menus and would include things like "About" or "Contact" pages.

The Django Admin includes a list filter to let you quickly sort Posts vs. Pages.



## Comments and Spam
Native vs. Disqus, Google, etc.


### Gravatar

Gravatar support in comment templates is present by default, and avatars are derived from the commenter's email, if they have a gravatar account:

`<img src="{{ comment.email|gravatar:60 }}" alt="" />`

The fallback icon is the class "Mystery Man" ("mm"). This can be changed to one of the [other defaults](https://en.gravatar.com/site/implement/images/) by changing the template tag itself (room for improvement there).

### Sanitizing Comments

Malicious HTML will be stripped from posted comments via `bleach`. The default set of allowed tags is:

`['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'strong', 'ul']`

To override, add to your project settings e.g.:

`BLEACH_ALLOWED_TAGS = ['hr', 'b', 'i']`

### Comment Moderation

View is at ...

By default, the emails of approved comments are added to an ApprovedCommentors table, and future comments from those email addresses will be auto-approved. To disable this setting, turn it off in the Admin config.


### Akismet Spam Checking

Because WordPress runs 20% of the internet, and Akismet is bundled with every WordPress installation, millions of users are constantly submitting spam and ham feedback to the Akismet service. Akismet is *incredibly* effective at spam control. Fortunatley, Akismet isn't tied to WordPress - it's available to anyone, and excellent Python libs exist for communicating with its API.

Tangerine includes native Akismet support. [Get a key](https://akismet.com/) (free or paid), add it to your Tangerine config, and enjoy virtually automatic spam control. In Tangerine's Comment Moderation interface, use the Spam/Ham buttons to help train Aksimet for the benefit of others.

n.b.: Marking a comment as spam/ham also toggles its Approved/Unapproved status. But toggling the approval status does *not* affect the spam status of the comment (because you might have good reasons to unapprove a comment on your site other than it being spam, or you might want to approve a comment that Akismet thinks is spam for some reason).

Devs who want to run the spam_checks pytest *must* add to their `test.py` settings:
AKISMET_KEY = 'abc123' and SITE_URL = 'https://your.registered.domain' (but with real values). Otherwise we can't run tests that call their API with YOUR credentials.

## Templates

The provided template examples are meant to represent "reasonable defaults" and to show most possible templatetag usages. By all means, rearrange and season to taste (copy templates dir into your project's templates dir and tweak).

### FIXME How to copy over and customize templates.

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

Define them in Admin, associate posts with categories when writing. A single post can be displayed in any number of categories.

To display a linked list of categories in your sidebar see the [Categories Template Tag documentation](#categories_tt).


<a name="date_archives"></a>
### Date Archives

You can view posts by time slices: year, year/month, and year/month/day, at URLs like:

```
/blog/2017  # Shows all posts published in 2017
/blog/2017/03  # Shows all posts published in March 2017
/blog/2017/03/24  # Shows all posts published on March 24, 2017
``` 

To display a hierarchical list of links to date archives in your sidebar, see the [date archives template tag](#date_archives_tt) documentation.


### Internal links

[Check this]

To link to any internal Post or Page, do this in a template:

`<a href="{% url 'tangerine:post_detail' 'about' %}">About</a>`

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

To run Tangerine's tests, add pytest to your virtualenv:
`pip install pytest` or `pipenv install pytest`
Then just run `pytest` from the projcect root.



### Extra JS

`{% block extra_js %}{% endblock extra_js %}`

We assume you have jquery installed!



## Adding Functionality

Tangerine does not (yet?) provide "plugin" capability like WordPress because we feel that most new functionality can be provided as a template tag created in your own app. Please see the template tags provided by Tangerine as examples, then create your customizations in your own app or project and load them into your template customizations. If you think others would benefit from the same functionality, make a pull request!

Functionality that cannot be provided by template tags should be submitted as a pull request to Tangerine. 



## Template Tags

Tangerine provides a native set of built-in template tags for the most common "sidebar" features used in blogs.

### Recent Comments Template Tag

Add to your base.html:


`{% block recent_comments %}{% endblock recent_comments %}`


Then call the `recent_comments` template tag from the template where you want recent comments to appear, with the number of comments you want to display:

```
{% get_recent_comments 10 as recent_comments %}
{# Now loop through recent_comments.comments #}

```

See `home.html` in the default theme for a usage example.


### RelatedLinkGroups Template Tag (blogroll)

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

<a name="date_archives_tt"></a>
### Date Archives Template Tag

To accompany Tangerine's support for [Date Archive](#date_archives) views, a template tag is provided to generate a list of links to date archive pages for which published posts actually exist. This template tag takes a start and end date, and can be configured to generate either a list of years or of months nested within years.

To enable date archive links in your sidebar, include a link to the template fragment in the parent template:

```
{% block date_archive %}
  {% include "tangerine/include/sidebar_date_archive.html" %}
{% endblock date_archive %}
```

Then call `get_date_archives` with a `dtype`, `start` and `end` where start and end are strings in format `YYYYMMDD`. Omit start and end to cover all time.

```
  {% load tangerine_tags %}

  {% with dtype='month' start='19000101' end='29160101' %}
    {% get_date_archives dtype=dtype start=start end=end as date_archives %}
  {% endwith %}
```

Then loop through `date_archives` in your template fragment.

See `include/sidebar_date_archives.html` in the reference theme for a full working example.

<a name="#categories_tt"></a>
### Categories Template Tag

Make sure your base template includes a block:

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


### Static files

Tangerine includes some CSS and Javascript for use in the management interface. To have Tangerine's static dir included in your project, add it to your project's `STATICFILES_DIRS `:

```
STATICFILES_DIRS = [
	...
    'tangerine/static'
]
```


### Custom URL Paths

Full list of URLs provided


### Author Pages


We provide an author page (in the admin) but if your site already has one, you can use that instead by changing the link in `tangerine/include/byline.html`.

---------

we do not provide a "themes" system because this app is meant to be dropped into an existing site. Theme your site, and let tangerine come along for the ride!

However, you will need the following CSS:

xxxxxxx

----------

Working with multiple blogs

Tangerine lets you create as many "blogs" (or news projects, or whatever you want to publish) within a single Django project, each with the same URLs sub-structor for categories, tags, date archives, etc. To accomplish this, your top-level `urls.py` should include something like:

```
path('<blog_slug>/', include('tangerine.urls', namespace='tangerine')),
```

Notice that the pating information comes before the include. When Django encounters this pattern, the blog_slug will be passed automatically to every view referenced in the included urls module. Each view then passes the `blog_slug` down into the templates it renders, which then in turn becomes available to the template tags being called. You'll also notice that all sub-objects -- Post, RelatedLinkGroups, Categories, etc. -- all have ForeignKey relationships to a parent Blog instance.

In essence, `blog_slug` becomes a semi-global variable available throughout the context and hierarchy of each blog instance.

Most template tags must be called with two slugs: The passed slug of the blog in which they should render, and the slug of the object being requested. For example, when calling the `get_related_links` tags, use:

```
{% get_related_links blog_slug=blog_slug related_links_slug=related_links_slug as link_group %}
```

And if you want to work with just one blog space? 

-------

For now, we support just one RelatedLinkGroup per blog

All plugins must filter for blog_slug, so they know which blog to gather data for.

-------

RSS feeds are automatically generated and provided for each blog. An RSS link is not provided, but an RSS discovery URL is present in the HTML header. If you want to provide a visible link, search for 'rss' in `tangerine/base.html` for an example of link construction.


-------

All views filter per-blog - none are global for all blogs (if you request a category view, and the same category exists in three blogs, you only get results for the current one).

If you want to see results for all posts in that category for ALL blogs, you must create your own view to do that. 

Likewise, the example search engine only searches through the current blog. If you want global search on your site, you'll need to implement that on your site in your own way. (n.b.: `ops.get_search_qs` does search all blogs, but it's filtered to the current blog in `views.search`, so `ops.get_search_qs` could be helpful for your global search. 

------

When deploying multiple blogs on the same project, all blogs will share the same URL structure, e.g. for the same category on two blogs "foo" and "bar":

http://example.com/foo/cat/bike
http://example.com/bar/cat/bike

or for date archives on two blogs:

http://example.com/foo/2017/11
http://example.com/bar/2017/11

It is not possible to have multiple blogs on the same project use different URL structures.

