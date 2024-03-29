import datetime

# from taggit.models import Tag

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect

from blog.tangerine.forms import CommentForm, CommentSearchForm
from blog.tangerine.models import Category, Post, Comment, Blog
from blog.tangerine.ops import toggle_approval, toggle_spam, process_comment, get_search_qs


def home(request, blog_slug):
    blog = get_object_or_404(Blog, slug=blog_slug)
    posts = Post.pub.filter(blog=blog)
    num_posts = blog.num_posts_per_list_view

    paginator = Paginator(posts, num_posts)
    page = request.GET.get("page")
    posts = paginator.get_page(page)

    return render(request, "tangerine/home.html", {"posts": posts, "blog_slug": blog_slug})


def post_detail(request, blog_slug, year, month, day, slug):
    post = get_object_or_404(
        Post,
        blog__slug=blog_slug,
        published=True,
        trashed=False,
        pub_date__year=year,
        pub_date__month=month,
        pub_date__day=day,
        slug=slug,
    )

    if request.method == "POST":
        form = CommentForm(request.POST)

        # Handle posted comment
        if form.is_valid():
            comment = form.save(commit=False)
            process_comment(request, comment, post)  # Bulk of comment processing happens here
            return HttpResponseRedirect(post.get_absolute_url())
        else:
            # We should never be here, given browser-side field validation ensuring required date # fields in correct
            # format. Users of very old browsers might have issues if they skip a required field.
            # print(form.errors)
            pass

    else:
        # For auth users, pre-populate form with known first/last name, email
        if request.user.is_authenticated:
            form = CommentForm(
                initial={"name": request.user.get_full_name, "email": request.user.email}
            )
        else:
            form = CommentForm()

    try:
        next_post = Post.get_next_by_pub_date(post, ptype="post")
    except Post.DoesNotExist:
        next_post = None
    try:
        previous_post = Post.get_previous_by_pub_date(post, ptype="post")
    except Post.DoesNotExist:
        previous_post = None

    return render(
        request,
        "tangerine/post_detail.html",
        {
            "post": post,
            "form": form,
            "next_post": next_post,
            "previous_post": previous_post,
            "blog_slug": blog_slug,
        },
    )


def page_detail(request, blog_slug, slug):
    post = get_object_or_404(Post, published=True, trashed=False, slug=slug)
    return render(request, "tangerine/post_detail.html", {"post": post, "blog_slug": blog_slug})


def category(request, blog_slug, cat_slug):
    # This view shows all posts in category `cat_slug` for the current blog
    blog = get_object_or_404(Blog, slug=blog_slug)
    cat = get_object_or_404(Category, slug=cat_slug, blog=blog)
    posts = Post.pub.filter(
        blog=blog,
        categories__in=[
            cat,
        ],
    ).order_by("-pub_date")

    num_posts = blog.num_posts_per_list_view
    paginator = Paginator(posts, num_posts)
    page = request.GET.get("page")
    posts = paginator.get_page(page)

    return render(
        request,
        "tangerine/category.html",
        {"category": cat, "posts": posts, "blog_slug": blog_slug},
    )


def tag(request, blog_slug, tag_slug):
    # This view shows all posts tagged with `tag_slug`
    blog = get_object_or_404(Blog, slug=blog_slug)
    # tag = get_object_or_404(Tag, slug=tag_slug)
    # posts = Post.pub.filter(blog=blog, tags__in=[tag, ]).order_by('-pub_date')
    posts = Post.pub.filter(
        blog=blog,
    ).order_by("-pub_date")

    num_posts = blog.num_posts_per_list_view
    paginator = Paginator(posts, num_posts)
    page = request.GET.get("page")
    posts = paginator.get_page(page)
    # FIXME: Can we re-use category.html here? Very similar.
    # return render(request, "tangerine/tag.html", {'tag':  tag, 'posts': posts, 'blog_slug': blog_slug})
    return render(request, "tangerine/tag.html", {"posts": posts, "blog_slug": blog_slug})


def date_archive(request, blog_slug, year, month=None, day=None):
    """Get posts by year | year and month | year and month and day."""

    blog = get_object_or_404(Blog, slug=blog_slug)
    posts = Post.pub.filter(blog=blog, pub_date__year=year).order_by("-pub_date")
    if month:
        posts = posts.filter(pub_date__month=month)
    if day:
        posts = posts.filter(pub_date__day=day)

    num_posts = blog.num_posts_per_list_view
    paginator = Paginator(posts, num_posts)
    page = request.GET.get("page")
    posts = paginator.get_page(page)

    # For use in template display, compose a proper date object from passed in params.
    # We always have year; If month or day are missing, sub in today's month/day.
    pseudo_month = month if month else datetime.date.today().month
    pseudo_day = day if day else datetime.date.today().day
    req_date = datetime.date(year=year, month=pseudo_month, day=pseudo_day)

    context = {
        "posts": posts,
        "year": year,
        "month": month,
        "day": day,
        "req_date": req_date,
        "blog_slug": blog_slug,
    }
    return render(request, "tangerine/date_archive.html", context)


def author(request, blog_slug, username):
    """Display bio, avatar, and previous posts for a given author"""

    user = get_object_or_404(get_user_model(), username=username)
    author_posts = Post.objects.filter(author=user).order_by("-pub_date")

    context = {"author": user.authorpage, "author_posts": author_posts, "blog_slug": blog_slug}
    return render(request, "tangerine/author.html", context)


def search(request, blog_slug):
    """Display results of search for Post or Page objects.
    FIXME: Currently searching all blogs. Should this be able to search just one blog at a time?"""

    if request.GET.get("q"):
        qs = get_search_qs(request.GET.get("q"))

    blog = get_object_or_404(Blog, slug=blog_slug)
    qs = qs.filter(blog=blog).order_by("-pub_date")

    paginator = Paginator(qs, 25)
    page = request.GET.get("page")
    posts = paginator.get_page(page)

    context = {"posts": posts, "q": request.GET.get("q"), "blog_slug": blog_slug}
    return render(request, "tangerine/search.html", context)


def feed(request, blog_slug):
    """Generate RSS 2 feed for the selected blog.
    Using standard view and template rather than Django RSS Feed class due to difficulty of passing in blog_slug
    for uniqueness of multiple feeds. Note `content_type` of return."""

    blog = get_object_or_404(Blog, slug=blog_slug)
    lang = settings.LANGUAGE_CODE
    posts = Post.pub.filter(blog=blog).order_by("-pub_date")[: blog.num_posts_per_list_view]
    site = get_current_site(request)

    context = {
        "blog": blog,
        "lang": lang,
        "site": site,
        "posts": posts,
    }

    return render(request, "tangerine/rss.xml", context, content_type="application/xhtml+xml")


# ===============  Private management interfaces  ===============


@user_passes_test(lambda u: u.is_superuser)
def manage_comments(request, comment_id=None):
    """Comment management interface. Same view is used for single comment moderation (if comment_id exists), or list."""

    if request.GET.get("q"):
        q = request.GET.get("q")
        comments = Comment.objects.filter(
            Q(body__icontains=q) | Q(name__icontains=q) | Q(email__icontains=q)
        )
    else:
        q = None
        comments = (
            Comment.objects.all()
        )  # In this view, don't filter for approved, spam etc. - show all.

    if comment_id:
        comments = comments.filter(id=comment_id)

    comments = comments.order_by("-created")
    form = CommentSearchForm(initial={"q": q})

    paginator = Paginator(comments, 25)  # Show num comments per page
    page = request.GET.get("page")
    comments = paginator.get_page(page)

    context = {
        "comments": comments,
        "form": form,
        "q": q,
    }
    return render(request, "tangerine/management/comments.html", context)


# ===============  Non-displaying view functions that redirect immediately without interaction  ===============


@user_passes_test(lambda u: u.is_superuser)
def toggle_comment_approval(request, comment_id):

    comment = get_object_or_404(Comment, id=comment_id)
    toggle_approval(comment)
    messages.add_message(
        request, messages.SUCCESS, "Approval status of comment {} changed.".format(comment.id)
    )

    return redirect("tangerine:manage_comments")


@user_passes_test(lambda u: u.is_superuser)
def toggle_comment_spam(request, comment_id):

    comment = get_object_or_404(Comment, id=comment_id)
    toggle_spam(comment)
    messages.add_message(
        request, messages.SUCCESS, "Spam status of comment {} changed.".format(comment.id)
    )

    return redirect("tangerine:manage_comments")


@user_passes_test(lambda u: u.is_superuser)
def delete_comment(request, comment_id):

    comment = get_object_or_404(Comment, id=comment_id)
    comment.delete()
    messages.add_message(request, messages.SUCCESS, "Comment deleted.")

    return redirect("tangerine:manage_comments")
