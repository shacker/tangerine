from django.contrib import admin


from tangerine.models import Category, Post, RelatedLinkGroup, RelatedLink, Config


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'slug',
        'published',
        'ptype',
        'created',
    )

    fields = (
        'title',
        'slug',
        'content',
        'summary',
        'author',
        'categories',
        'published',
        'pub_date',
        'trashed',
        'ptype',
    )
    list_filter = ['published', 'ptype', 'trashed', ]
    search_fields = ['title', 'content', 'summary', ]
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ('categories',)


class RelatedLinkInline(admin.TabularInline):
    model = RelatedLink
    extra = 1


class RelatedLinkGroupAdmin(admin.ModelAdmin):
    inlines = [RelatedLinkInline, ]


admin.site.register(Config)
admin.site.register(Category)
admin.site.register(Post, PostAdmin)
admin.site.register(RelatedLinkGroup, RelatedLinkGroupAdmin)
