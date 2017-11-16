import pwd
import os

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model

from tangerine.factories import CategoryFactory, PostFactory
from tangerine.models import Category


def gen_su():
    # Generate a superuser for local developer, if needed
    username = pwd.getpwuid(os.geteuid()).pw_name
    if not get_user_model().objects.filter(username=username).exists():
        print("Creating a superuser for YOU.")
        fname = input("First name: ")
        lname = input("Last name: ")
        email = input("Email: ")
        get_user_model().objects.create(
            username=username, is_superuser=True, is_staff=True,
            first_name=fname, last_name=lname, email="{e}".format(u=username, e=email))
        print("Created user {}. Run `./manage.py changepassword` to set your password.".format(username))


class Command(BaseCommand):
    help = "For use in development only: Create some fake categories and <num_posts> fake posts via FactoryBoy."

    def __init__(self):
        self.num_posts = 10  # Number of fake posts to be created per category.

    def handle(self, *args, **options):

        if not get_user_model().objects.all():
            gen_su()  # Create a superuser and make them author of all posts

        author = get_user_model().objects.order_by('?').first()

        cats = ['Family', 'Coding', 'Environment', 'Culture', 'Politics', 'Bike', 'Photography', ]
        if not Category.objects.all().count():
            for cat_title in cats:
                cat = CategoryFactory.create(title=cat_title)
                for _ in range(5):
                    p = PostFactory(author=author)
                    p.categories.add(cat)
                print("Five fake posts in category {} created.".format(cat_title))

        # Set up starter About page and RelatedLinks to work with default template
        call_command('loaddata', 'about')
        call_command('loaddata', 'related_links')

        print("Starter set of RelatedLinks \"blogroll\" created.")
