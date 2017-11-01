from django.shortcuts import render, get_object_or_404


from blog.models import Post


def home(request):
    posts = Post.pub.order_by('-created')
    return render(request, "blog/home.html", {'posts': posts})


def post_detail(request, year, month, slug):
    post = get_object_or_404(Post, created__year=year, created__month=month, slug=slug)
    return render(request, "blog/post_detail.html", {'post': post})
