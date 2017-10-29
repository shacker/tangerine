import factory
from faker import Faker

from django.utils.text import slugify

from .models import Category, Post
from users.models import User


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post
        django_get_or_create = ('slug', )

    title = factory.Faker('text', max_nb_chars=48)
    slug = factory.LazyAttribute(lambda o: slugify(o.title)[:48])
    content = factory.Faker('text', max_nb_chars=1400)
    summary = factory.Faker('text')

    @factory.post_generation
    def set_author(self, build, extracted, **kwargs):
        a = User.objects.all().order_by('?').first()  # Select random author
        self.author = a

    @factory.post_generation
    def set_cats(self, build, extracted, **kwargs):
        c = Category.objects.all().order_by('?').first()  # Select random category
        self.categories.add(c)

    @factory.post_generation
    def set_created(self, build, extracted, **kwargs):
        fake = Faker()
        self.created = fake.date_this_decade()
