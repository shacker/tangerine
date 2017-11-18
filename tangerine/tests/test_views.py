from django.urls import reverse

from test_plus.test import TestCase

from tangerine.factories import CategoryFactory, PostFactory, ConfigFactory


class BaseUserTestCase(TestCase):

    def setUp(self):
        ConfigFactory()

        self.user1 = self.make_user("user1")

        self.post1 = PostFactory(slug="somepost")
        cat = CategoryFactory(slug="somecat")
        self.post1.categories.add(cat)

        self.post2 = PostFactory(slug="someotherpost")  # Has no category


class TestPosts(BaseUserTestCase):
    '''View tests for posts'''

    def test_good_slug_good_view(self):
        with self.login(username=self.user1.username):
            url = self.post1.get_absolute_url()
            response = self.get(url)
            self.response_200(response)

    def test_bad_slug_404(self):
        url = reverse('tangerine:post_detail', kwargs={'year': 2002, 'month': 7, 'day': 23, 'slug': "whatever"})
        response = self.get(url)
        self.response_404(response)
