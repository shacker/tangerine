from django.contrib.syndication.views import Feed
from tangerine.models import Post, Config


class LatestEntriesFeed(Feed):
    config = Config.objects.first()
    title = config.site_title
    description = config.tagline
    link = config.site_url

    def items(self):
        return Post.pub.all()[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        if item.summary:
            _desc = item.summary
        else:
            _desc = item.content
        return _desc

    # No need for `item_link` since Post has a get_absolute_url method.
