import factory

from django.contrib.auth import get_user_model


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()
        django_get_or_create = ('username', )

    username = factory.LazyAttribute(lambda o: "{}_{}_fake".format(o.first_name.lower(), o.last_name.lower()))
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    is_superuser = factory.Faker('boolean', chance_of_getting_true=10)
    is_staff = factory.Faker('boolean', chance_of_getting_true=10)
