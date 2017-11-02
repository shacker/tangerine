# Tangerine

## Super-clean Django blogging system

*Just the bits you need, nothing more.*

**Supports:**

- Post lists/detail/permalink views
- Tags and categories with views
- Spam-filtered commenting
- User-created themes
- Author profiles
- Syntax highlighting for code samples
- "Trash" system
- List view pagination
- WordPress importer
- Blogroll system
- OEmbed support
- Navigation system
- Search
- Rich text editor
- Configurable via admin:
    - Site title
    - Selected theme
    - Favico
    - Num posts per list view

**Assumes:**
- Python 3.5+
- Pipenv

### Installation

- Create Pipenv
    - Notes
- `pipenv install`
    - Notes
- Create local.py
- `./manage.py migrate`
- `npm install`
- In admin, select a Theme (or use Default)

Be sure to set your timezone in settings:

`TIME_ZONE = 'America/Los_Angeles'`

You can list all the available timezones with:

```
pytz.all_timezones:
import pytz
pytz.all_timezones
```
### Initial data

During development, you may want a bunch of Categories and Posts to work with so you know what things will look like.

After creating some categories manually, use this to create 500 faked posts for testing purposes:

`./manage.py fake_posts`

 You might want to rename or delete fake categories after initial creation.

### Create your own theme

### Finding 3rd-party themes
