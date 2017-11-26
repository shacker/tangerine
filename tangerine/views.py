from ipware.ip import get_ip

from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect

from tangerine.forms import CommentForm
from tangerine.models import Category, Post, Comment, Config
from tangerine.utils import sanitize_comment, get_comment_approval, toggle_approval, spam_checks


def home(request):
    posts = Post.pub.all()

    num_posts = Config.objects.first().num_posts_per_list_view
    paginator = Paginator(posts, num_posts)
    page = request.GET.get('page')
    posts = paginator.get_page(page)

    return render(request, "tangerine/home.html", {'posts': posts})


def post_detail(request, year, month, day, slug):
    post = get_object_or_404(
        Post, published=True, trashed=False, created__year=year, created__month=month, created__day=day, slug=slug)

    if request.method == 'POST':
        form = CommentForm(request.POST)

        if form.is_valid():

            comment = form.save(commit=False)

            if request.user.is_authenticated:
                comment.author = request.user
                comment.name = request.user.get_full_name()
                comment.email = request.user.email

            # Is this a threaded comment?
            if request.POST.get('parent_id'):
                comment.parent = Comment.objects.get(id=request.POST.get('parent_id'))

            # If commenter is logged in, override name and email with stored values from User object
            if request.user.is_authenticated:
                comment.name = request.user.get_full_name()
                comment.email = request.user.email

            # Set required relationship to Post object
            comment.post = post

            # Get commenter's IP and User-Agent string
            ip = get_ip(request)
            if ip is not None:
                comment.ip_address = ip
            comment.user_agent = request.META.get('HTTP_USER_AGENT', '')

            comment.spam = spam_checks(comment)

            # Strip disallowed HTML tags. See tangerine docs to customize.
            comment.body = sanitize_comment(form.cleaned_data['body'])

            # Call comment approval workflow
            comment.approved = get_comment_approval(comment.email, request.user.is_authenticated)
            if comment.approved:
                messages.add_message(request, messages.SUCCESS, 'Your comment has been posted.')
            else:
                messages.add_message(request, messages.INFO, 'Your comment has been held for moderation.')

            comment.save()

            return HttpResponseRedirect(post.get_absolute_url())

    else:
        form = CommentForm()

    try:
        next_post = Post.get_next_by_created(post, ptype='post')
    except Post.DoesNotExist:
        next_post = None
    try:
        previous_post = Post.get_previous_by_created(post, ptype='post')
    except Post.DoesNotExist:
        previous_post = None

    return render(request, "tangerine/post_detail.html", {
        'post': post,
        'form': form,
        'next_post': next_post,
        'previous_post': previous_post
    })


def page_detail(request, slug):
    post = get_object_or_404(Post, published=True, trashed=False, slug=slug)
    return render(request, "tangerine/post_detail.html", {'post': post})


def category(request, cat_slug):
    cat = get_object_or_404(Category, slug=cat_slug)
    posts = Post.pub.filter(categories__in=[cat, ])
    return render(request, "tangerine/category.html", {'category':  cat, 'posts': posts})


# ===============  Management interfaces  ===============


def manage_comments(request):
    comments = Comment.objects.all()

    paginator = Paginator(comments, 25)  # Show num contacts per page
    page = request.GET.get('page')
    comments = paginator.get_page(page)

    return render(request, "tangerine/management/comments.html", {'comments': comments, })


def toggle_comment_approval(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    # Work is done in utility function.
    toggle_approval(comment)
    messages.add_message(request, messages.SUCCESS, 'Approval status of comment {} changed.'.format(comment.id))

    return redirect('tangerine:manage_comments')
