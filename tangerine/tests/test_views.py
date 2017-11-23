import pytest

from django.urls import reverse

from test_plus.test import TestCase

from tangerine.factories import CategoryFactory, PostFactory, ConfigFactory
from tangerine.models import Comment


class BaseUserTestCase(TestCase):

    def setUp(self):
        ConfigFactory()

        self.user1 = self.make_user(username="user1")
        self.user1.first_name = "Elmo"
        self.user1.last_name = "James"
        self.user1.email = "x@y.com"
        self.user1.save()

        self.post1 = PostFactory(slug="somepost")
        cat = CategoryFactory(slug="somecat")
        self.post1.categories.add(cat)

        self.post2 = PostFactory(slug="someotherpost")  # Has no category

        self.comment_data = {
            'name': ['Duke Ellington'],
            'email': ['a@b.com'],
            'website': ['http://example.com'],
            'body': ['some content']
        }


class TestNoConfig(TestCase):
    # Accessing any page without having set up a Config object should throw an exception.
    # Note we inherit from TestCase here to *avoid* setting up the Config object.

    def test_no_config(self):
        with pytest.raises(AttributeError) as excinfo:
            url = reverse('tangerine:home')
            self.get(url)
        assert 'AttributeError' in str(excinfo)


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


class TestComments(BaseUserTestCase):
    # Comment threading is initiated in templates, so we can only test threaded comment posting from the view (here).

    def test_top_level_comment_no_auth(self):
        # For unauthenticated users, we store the name and email
        url = self.post1.get_absolute_url()
        response = self.post(url, data=self.comment_data)
        self.response_302(response)
        new_comment = Comment.objects.filter(post=self.post1).first()  # Doesn't mean approved, just that it exists.
        assert new_comment.name == self.comment_data.get('name')[0]
        assert new_comment.email == self.comment_data.get('email')[0]
        assert new_comment.website == self.comment_data.get('website')[0]
        assert new_comment.body == self.comment_data.get('body')[0]

    def test_top_level_comment_auth(self):
        # For authenticated users, we store a FK to User on the `author` field.
        with self.login(username=self.user1.username):
            url = self.post1.get_absolute_url()
            self.post(url, data=self.comment_data)
            new_comment = Comment.objects.filter(post=self.post1).first()
            assert new_comment.author == self.user1

            # Even though self.comment_data includes Name and Email fields,
            # the view sets their name email fields to those of the authenticated user.
            # On the actual form, name and email fields are hidden for auth user,
            # and the view logic overrides name and email.
            assert new_comment.name == self.user1.get_full_name()
            assert new_comment.email == self.user1.email

    def test_threaded_comment(self):
        # If posting a threaded comment, new comment should be stored as child of parent
        with self.login(username=self.user1.username):
            url = self.post1.get_absolute_url()
            self.post(url, data=self.comment_data)  # Make parent comment first
            new_comment_data = self.comment_data
            parent_id = Comment.objects.first().id
            new_comment_data['parent_id'] = parent_id
            new_comment_data['body'] = 'xyz'

            # Post child comment, then get both back from the db. Intended child/parent relation is preserved
            self.post(url, data=new_comment_data)
            orig_comment = Comment.objects.get(id=parent_id)
            child_comment = orig_comment.child_comments().first()
            assert child_comment.parent.id == orig_comment.id
            assert child_comment.body == 'xyz'
