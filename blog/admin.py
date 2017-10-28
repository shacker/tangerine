from django.contrib import admin

from blog.models import Category, Post


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'slug',
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
    )
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ('categories',)

admin.site.register(Category)
admin.site.register(Post, PostAdmin)
