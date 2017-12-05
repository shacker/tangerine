from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect

from tangerine.forms import CommentForm, CommentSearchForm
from tangerine.models import Category, Post, Comment, Config
from tangerine.utils import toggle_approval, toggle_spam, process_comment


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
            process_comment(request, comment, post)  # Bulk of comment processing happens here
            return HttpResponseRedirect(post.get_absolute_url())
        else:
            # We should never be here, given browser-side field validation.
            # Users of very old browsers might have issues if they skip a required field.
            # print(form.errors)
            pass

    else:
        # For auth users, pre-populate form with known first/last name, email
        if request.user.is_authenticated:
            form = CommentForm(initial={'name': request.user.get_full_name, 'email': request.user.email})
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


# ===============  Private management interfaces  ===============

@user_passes_test(lambda u: u.is_superuser)
def manage_comments(request, comment_id=None):
    """Comment management interface. Same view is used for single comment moderation (if comment_id exists), or list."""
    config = Config.objects.first()

    if request.GET.get('q'):
        q = request.GET.get('q')
        comments = Comment.objects.filter(
            Q(body__icontains=q) |
            Q(name__icontains=q) |
            Q(email__icontains=q)
        )
    else:
        q = None
        comments = Comment.objects.all()  # In this view, don't filter for approved, spam etc. - show all.

    if comment_id:
        comments = comments.filter(id=comment_id)

    comments = comments.order_by('-created')
    form = CommentSearchForm(initial={'q': q})

    paginator = Paginator(comments, 25)  # Show num comments per page
    page = request.GET.get('page')
    comments = paginator.get_page(page)

    context = {'comments': comments, 'form': form, 'q': q, 'config': config}
    return render(request, "tangerine/management/comments.html", context)


# ===============  Non-displaying process functions  ===============


@user_passes_test(lambda u: u.is_superuser)
def toggle_comment_approval(request, comment_id):

    comment = get_object_or_404(Comment, id=comment_id)
    toggle_approval(comment)
    messages.add_message(request, messages.SUCCESS, 'Approval status of comment {} changed.'.format(comment.id))

    return redirect('tangerine:manage_comments')


@user_passes_test(lambda u: u.is_superuser)
def toggle_comment_spam(request, comment_id):

    comment = get_object_or_404(Comment, id=comment_id)
    toggle_spam(comment)
    messages.add_message(request, messages.SUCCESS, 'Spam status of comment {} changed.'.format(comment.id))

    return redirect('tangerine:manage_comments')


@user_passes_test(lambda u: u.is_superuser)
def delete_comment(request, comment_id):

    comment = get_object_or_404(Comment, id=comment_id)
    comment.delete()
    messages.add_message(request, messages.SUCCESS, 'Comment deleted.')

    return redirect('tangerine:manage_comments')
