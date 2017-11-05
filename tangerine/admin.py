from django.contrib import admin

from adminsortable.admin import NonSortableParentAdmin, SortableStackedInline

from tangerine.models import Category, Post, RelatedLinkGroup, RelatedLink


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'slug',
        'published',
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
    )
    list_filter = ['published', 'trashed', ]
    search_fields = ['title', 'content', 'summary', ]
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ('categories',)


class RelatedLinkInline(SortableStackedInline):
    model = RelatedLink
    extra = 1


class RelatedLinkGroupAdmin(NonSortableParentAdmin):
    inlines = [RelatedLinkInline]


admin.site.register(Category)
admin.site.register(Post, PostAdmin)
admin.site.register(RelatedLinkGroup, RelatedLinkGroupAdmin)
