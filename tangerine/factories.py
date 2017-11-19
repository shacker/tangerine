import factory
import pytz
from faker import Faker
from titlecase import titlecase

from django.utils.text import slugify

from .models import Category, Post, RelatedLinkGroup, RelatedLink, Config, Comment
from users.models import User


def gen_headline():
    # faker doesn't provide a way to generate headlines in Title Case, without periods, so make our own.
    fake = Faker()
    return titlecase(fake.text(max_nb_chars=48).rstrip('.'))


def gen_html_content():
    # faker doesn't provide raw html text, so convert the output of fake.paragraphs()
    fake = Faker()
    grafs = fake.paragraphs()
    htmlstr = ''
    for g in grafs:
        htmlstr += "<p>{}</p>\n\n".format(g)
    return htmlstr


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
    content = factory.LazyAttribute(lambda o: gen_html_content())
    summary = factory.Faker('text')

    @factory.post_generation
    def set_author(self, build, extracted, **kwargs):
        a = User.objects.all().order_by('?').first()  # Select random author
        self.author = a

    @factory.post_generation
    def set_created(self, build, extracted, **kwargs):
        fake = Faker()
        self.created = fake.date_time_this_decade(tzinfo=pytz.UTC)


class CommentFactory(factory.django.DjangoModelFactory):
    # MUST be called with a Post object
    class Meta:
        model = Comment

    approved = factory.LazyAttribute(lambda o: True)
    body = factory.LazyAttribute(lambda o: gen_html_content())
    email = factory.Faker('safe_email')
    name = factory.Faker('name')
    website = factory.Faker('url')


class RelatedLinkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RelatedLink

    # Must pass in a RelatedLinkGroup as group= when instantiating
    # i.e. Most useful when instantiating a RelatedLinkGroupFactory
    site_title = factory.Faker('company')
    site_url = factory.Faker('url')


class RelatedLinkGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RelatedLinkGroup
        django_get_or_create = ('slug', )

    slug = factory.Faker('words', nb=1)

    @factory.post_generation
    # Create related links
    def related_links(self, build, extracted, **kwargs):
        RelatedLinkFactory.create_batch(5, group=self)


class ConfigFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Config

    site_title = factory.Faker('catch_phrase')
    tagline = factory.Faker('words', nb=5)
