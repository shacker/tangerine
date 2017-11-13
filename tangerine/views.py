from django.shortcuts import render, get_object_or_404

from tangerine.models import Category, Post


def home(request):
    posts = Post.pub.all()
    return render(request, "tangerine/home.html", {'posts': posts})


def post_detail(request, year, month, day, slug):
    post = get_object_or_404(
        Post, published=True, trashed=False, created__year=year, created__month=month, created__day=day, slug=slug)
    return render(request, "tangerine/post_detail.html", {'post': post})


def page_detail(request, slug):
    post = get_object_or_404(Post, published=True, trashed=False, slug=slug)
    return render(request, "tangerine/post_detail.html", {'post': post})


def category(request, cat_slug):
    cat = get_object_or_404(Category, slug=cat_slug)
    posts = Post.pub.filter(categories__in=[cat, ])
    return render(request, "tangerine/category.html", {'category':  cat, 'posts': posts})
