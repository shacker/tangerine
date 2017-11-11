import pwd
import os

from django.core.management.base import BaseCommand
from django.core.management import call_command

from tangerine.factories import CategoryFactory, PostFactory
from tangerine.models import Category

from users.factories import UserFactory
from users.models import User


def gen_su():
    # Generate a superuser for local developer, if needed
    username = pwd.getpwuid(os.geteuid()).pw_name
    if not User.objects.filter(username=username).exists():
        print("Creating a superuser for YOU.")
        fname = input("First name: ")
        lname = input("Last name: ")
        email = input("Email: ")
        UserFactory(
            username=username, is_superuser=True, is_staff=True,
            first_name=fname, last_name=lname, email="{e}".format(u=username, e=email))
        print("Created user {}. Run `./manage.py changepassword` to set your password.".format(username))


class Command(BaseCommand):
    help = "For use in development only: Create some fake categories and <num_posts> fake posts via FactoryBoy."

    def __init__(self):
        self.num_posts = 50

    def handle(self, *args, **options):

        if not User.objects.all():
            gen_su()  # Create a superuser and make them author of all posts

        cats = ['Family', 'Coding', 'Environment', 'Culture', 'Politics', 'Bike', 'Photography', ]
        if not Category.objects.all().count():
            for c in cats:
                CategoryFactory.create(title=c)
            print("{} fake categories created.".format(len(cats)))

        author = User.objects.order_by('?').first()
        PostFactory.create_batch(self.num_posts, author=author)
        print("{} fake posts created.".format(self.num_posts))

        # Set up starter RelatedLinks to work with default template
        call_command('related_links')
        print("Starter set of RelatedLinks \"blogroll\" created.")
