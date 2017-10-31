from django.core.management.base import BaseCommand

from blog.factories import CategoryFactory, PostFactory
from blog.models import Category


class Command(BaseCommand):
    help = "For use in development only: Create some fake categories and <num_posts> fake posts via FactoryBoy."

    def __init__(self):
        self.num_posts = 50

    def handle(self, *args, **options):

        cats = ['Family', 'Coding', 'Environment', 'Culture', 'Politics', 'Bike', 'Photography', ]
        if not Category.objects.all().count():
            for c in cats:
                CategoryFactory.create(title=c)
                print("{} fake categories created.".format(len(cats)))

        PostFactory.create_batch(self.num_posts)
        print("{} fake posts created.".format(self.num_posts))
