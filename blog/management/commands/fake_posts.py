import pwd
import os
import sys

from django.core.management.base import BaseCommand

from blog.factories import CategoryFactory, PostFactory
from blog.models import Category

from users.factories import UserFactory
from users.models import User


def gen_su():
    # Generate a superuser for local developer, if needed
    username = pwd.getpwuid(os.geteuid()).pw_name
    if not User.objects.filter(username=username).exists():
        print("Creating a superuser for YOU.")
        fname = input("First name: ")
        lname = input("Last name: ")
        UserFactory(
            username=username, is_superuser=True, is_staff=True,
            first_name=fname, last_name=lname, email="{u}@energy-solution.com".format(u=username))
        print("Created user {}. Run `./manage.py changepassword` to set your password.".format(username))


class Command(BaseCommand):
    help = "For use in development only: Create some fake categories and <num_posts> fake posts via FactoryBoy."

    def __init__(self):
        self.num_posts = 50

    def handle(self, *args, **options):

        if not User.objects.all():
            gen_su()

        cats = ['Family', 'Coding', 'Environment', 'Culture', 'Politics', 'Bike', 'Photography', ]
        if not Category.objects.all().count():
            for c in cats:
                CategoryFactory.create(title=c)
            print("{} fake categories created.".format(len(cats)))

        author = User.objects.order_by('?').first()
        PostFactory.create_batch(self.num_posts, author=author)
        print("{} fake posts created.".format(self.num_posts))
