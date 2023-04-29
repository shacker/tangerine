from django.contrib import admin
from django.utils.html import strip_tags


from tangerine.models import (
    Category,
    Post,
    RelatedLinkGroup,
    RelatedLink,
    Blog,
    Comment,
    AuthorPage,
)


class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "slug",
        "blog",
        "published",
        "ptype",
        "pub_date",
    )

    fields = (
        "title",
        "slug",
        "blog",
        "content",
        "summary",
        "author",
        "categories",
        "published",
        "pub_date",
        "trashed",
        "ptype",
        "tags",
    )

    list_filter = [
        "published",
        "ptype",
        "trashed",
    ]
    search_fields = [
        "title",
        "content",
        "summary",
    ]
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("categories",)


class RelatedLinkInline(admin.TabularInline):
    model = RelatedLink
    extra = 1


class RelatedLinkGroupAdmin(admin.ModelAdmin):
    inlines = [
        RelatedLinkInline,
    ]
    list_display = ["blog"]


def comment_body_intro(obj):
    # Truncate comment body for display in the admin
    return strip_tags(obj.body[:20])


class CategoryAdmin(admin.ModelAdmin):
    list_display = ["title", "blog"]


class CommentAdmin(admin.ModelAdmin):
    raw_id_fields = ("post", "parent", "author")

    list_display = (
        comment_body_intro,
        "post",
        "author",
        "name",
        "email",
        "created",
        "approved",
    )
    list_filter = [
        "approved",
    ]


class BlogAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("title", "slug", "tagline", "from_email")}),
        (
            "Posts",
            {
                "fields": ("num_posts_per_list_view", "show_future"),
            },
        ),
        (
            "Comments",
            {
                "fields": (
                    "comment_system",
                    "enable_comments_global",
                    "auto_approve_previous_commentors",
                    "moderation_email",
                ),
            },
        ),
        (
            "External",
            {
                "fields": (
                    "google_analytics_id",
                    "akismet_key",
                ),
            },
        ),
    )


admin.site.register(Blog, BlogAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(AuthorPage)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(RelatedLinkGroup, RelatedLinkGroupAdmin)
