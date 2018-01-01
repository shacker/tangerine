import pytest

from django.urls import reverse

from tangerine.factories import CategoryFactory, PostFactory, ConfigFactory
from tangerine.models import Comment


@pytest.fixture
def config():
    # Set up base configuration data (site title, etc.)
    ConfigFactory()


@pytest.fixture
def post1():
    # Create post with category.
    post1 = PostFactory(slug="somepost")
    cat = CategoryFactory(slug="somecat")
    post1.categories.add(cat)
    return post1


@pytest.fixture
def comment_data():
    # Sample data for test comments
    return {
        'name': ['Duke Ellington'],
        'email': ['a@b.com'],
        'website': ['http://example.com'],
        'body': ['some content']
    }


@pytest.mark.django_db
def test_no_config(client):
    # *Don't* use config fixture to *avoid* setting up the Config object.
    # Accessing any page without having set up a Config object should throw an exception.
    with pytest.raises(AttributeError) as excinfo:
        url = reverse('tangerine:home')
        client.get(url)
    assert 'AttributeError' in str(excinfo)


@pytest.mark.django_db
def test_good_slug_good_view(config, post1, client):
    url = post1.get_absolute_url()
    response = client.get(url)
    assert response.status_code == 200  # Not redirected


@pytest.mark.django_db
def test_bad_slug_404(config, client):
    url = reverse('tangerine:post_detail', kwargs={'year': 2002, 'month': 7, 'day': 23, 'slug': "whatever"})
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_top_level_comment_no_auth(config, comment_data, post1, client):
    # Comment threading is initiated in templates, so we don't have unit tests for threaded comment posting - just this.
    # For unauthenticated users, we store the name and email.
    url = post1.get_absolute_url()
    response = client.post(url, data=comment_data)
    assert response.status_code == 302  # Redirect to the same view

    # Below doesn't mean comment is approved, just that it exists with correct data
    new_comment = Comment.objects.filter(post=post1).first()
    assert new_comment.name == comment_data.get('name')[0]
    assert new_comment.email == comment_data.get('email')[0]
    assert new_comment.website == comment_data.get('website')[0]
    assert new_comment.body == comment_data.get('body')[0]


@pytest.mark.django_db
def test_top_level_comment_auth(config, comment_data, post1, admin_user, admin_client):
    # For authenticated users, we store a FK to User on the `author` field.
    url = post1.get_absolute_url()
    admin_client.post(url, data=comment_data)
    new_comment = Comment.objects.filter(post=post1).first()
    assert new_comment.author == admin_user

    # Even though `comment_data` includes Name and Email fields,
    # the view sets their name email fields to those of the authenticated user.
    # On the actual form, name and email fields are hidden for auth user,
    # and the view logic overrides name and email.
    assert new_comment.name == admin_user.get_full_name()
    assert new_comment.email == admin_user.email


@pytest.mark.django_db
def test_threaded_comment(config, comment_data, post1, admin_user, admin_client):
    # If posting a threaded comment, new comment should be stored as child of parent
    url = post1.get_absolute_url()
    admin_client.post(url, data=comment_data)  # Make parent comment first
    new_comment_data = comment_data  # Re-use comment_data for child comment.
    parent_id = Comment.objects.first().id
    new_comment_data['parent_id'] = parent_id
    new_comment_data['body'] = 'xyz'

    # Post child comment, then get both back from the db. Intended child/parent relation is preserved.
    admin_client.post(url, data=new_comment_data)
    orig_comment = Comment.objects.get(id=parent_id)
    child_comment = orig_comment.child_comments().first()
    assert child_comment.parent.id == orig_comment.id
    assert child_comment.body == 'xyz'
