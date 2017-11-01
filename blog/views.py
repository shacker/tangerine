from django.shortcuts import render, get_object_or_404


from blog.models import Category, Post


def home(request):
    posts = Post.pub.order_by('-created')
    return render(request, "blog/home.html", {'posts': posts})


def post_detail(request, year, month, slug):
    post = get_object_or_404(Post, created__year=year, created__month=month, slug=slug)
    return render(request, "blog/post_detail.html", {'post': post})


def category(request, cat_slug):
    cat = Category.objects.get(slug=cat_slug)
    posts = Post.pub.filter(categories__in=[cat, ])
    return render(request, "blog/category.html", {'category':  cat, 'posts': posts})
