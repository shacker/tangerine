from django.urls import path

from tangerine import views

app_name = 'tangerine'

# Paths for public interface
urlpatterns = [

    path(
        '<int:year>/<int:month>/<int:day>/<slug:slug>/',
        views.post_detail,
        name="post_detail"),

    # Three possible URL formats for date_archive.
    path(
        '<int:year>/<int:month>/<int:day>/',
        views.date_archive,
        name="date_archive"),

    path(
        '<int:year>/<int:month>/',
        views.date_archive,
        name="date_archive"),

    path(
        '<int:year>/',
        views.date_archive,
        name="date_archive"),

    path(
        'cat/<str:cat_slug>/',
        views.category,
        name="category"),

    path(
        '<str:slug>/',
        views.page_detail,
        name="page_detail"),

    path(
        'search',
        views.search,
        name="search"),

    path(
        '',
        views.home,
        name="home"),


    #  ##################
    # Paths for management interface
    # Same view handles single comment moderation or list view
    path(
        'manage/comments/<int:comment_id>',
        views.manage_comments,
        name="manage_comment"),

    path(
        'manage/comments',
        views.manage_comments,
        name="manage_comments"),

    path(
        'manage/comments/toggle_approval/<int:comment_id>/',
        views.toggle_comment_approval,
        name="toggle_comment_approval"),

    path(
        'manage/comments/toggle_spam/<int:comment_id>/',
        views.toggle_comment_spam,
        name="toggle_comment_spam"),

    path(
        'manage/comments/delete_comment/<int:comment_id>/',
        views.delete_comment,
        name="delete_comment"),
]
