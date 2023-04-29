import pwd
import os
import random

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model

from tangerine.factories import (
    CategoryFactory,
    PostFactory,
    BlogFactory,
    CommentFactory,
    AuthorPageFactory,
)
from tangerine.models import Blog, AuthorPage


def gen_su():
    # Generate a superuser for local developer, if needed
    username = pwd.getpwuid(os.geteuid()).pw_name
    if not get_user_model().objects.filter(username=username).exists():
        print("Creating a superuser for YOU.")
        fname = input("First name: ")
        lname = input("Last name: ")
        email = input("Email: ")
        get_user_model().objects.create(
            username=username,
            is_superuser=True,
            is_staff=True,
            first_name=fname,
            last_name=lname,
            email="{e}".format(u=username, e=email),
        )
        call_command("changepassword")
        print("Created user {}.".format(username))


class Command(BaseCommand):
    help = "For use in development only: Create some fake categories and <num_posts> fake posts via FactoryBoy."

    def __init__(self):
        self.num_posts = 10  # Number of fake posts to be created per category.

    def handle(self, *args, **options):
        def create_cats_posts_comments(blog, cats):
            # Given a Blog object and a list of category titles, generate Categories full of Posts with Comments.
            for cat_title in cats:
                cat = CategoryFactory.create(blog=blog, title=cat_title)
                for _ in range(5):
                    p = PostFactory(blog=blog, author=author)
                    p.categories.add(cat)
                    CommentFactory.create_batch(random.randint(0, 10), post=p)
                print(
                    'Fake posts and comments in blog "{}" created (category "{}")'.format(
                        blog.title, cat_title
                    )
                )

        if not get_user_model().objects.all():
            gen_su()  # Create a superuser and make them author of all posts

        # For simplicity, all posts will have the same author.
        author = get_user_model().objects.order_by("?").first()
        if not AuthorPage.objects.filter(user=author).exists():
            AuthorPageFactory.create(user=author)

        # Create two fake Blogs for dummy content
        BlogFactory.create_batch(2)

        blog = Blog.objects.first()
        cats = [
            "Family",
            "Coding",
            "Environment",
            "Culture",
            "Politics",
            "Bike",
            "Photography",
        ]
        create_cats_posts_comments(blog, cats)

        blog = Blog.objects.last()
        cats = [
            "Audio",
            "Engineering",
            "Bioethics",
            "Bears",
            "Fishing",
            "Electric Vehicles",
        ]
        create_cats_posts_comments(blog, cats)

        # Set up starter About page and RelatedLinks to work with default template
        call_command("loaddata", "about")
        call_command("loaddata", "related_links")

        print("Starter sets of RelatedLinks created for each blog.")
