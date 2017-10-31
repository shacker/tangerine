import factory
import pytz
from faker import Faker
from titlecase import titlecase

from django.utils.text import slugify

from .models import Category, Post
from users.models import User


def gen_headline():
    # faker doesn't provide a way to generate headlines in Title Case, without periods, so make our own.
    fake = Faker()
    return titlecase(fake.text(max_nb_chars=48).rstrip('.'))


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
        django_get_or_create = ('slug', )

    title = factory.Faker('catch_phrase')
    slug = factory.LazyAttribute(lambda o: slugify(o.title)[:20])


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post
        django_get_or_create = ('slug', )

    title = factory.LazyAttribute(lambda o: gen_headline())
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
        self.created = fake.date_time_this_decade(tzinfo=pytz.UTC)
