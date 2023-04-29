import datetime
import pytest

from django.urls import reverse
from django.utils.timezone import make_aware

from tangerine.factories import CategoryFactory, PostFactory, ConfigFactory, CommentFactory
from tangerine.models import Post, Comment


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
        "name": ["Duke Ellington"],
        "email": ["a@b.com"],
        "website": ["http://example.com"],
        "body": ["some content"],
    }


@pytest.fixture
def posts_with_comments():
    PostFactory.create_batch(3)
    for p in Post.objects.all():
        CommentFactory(post=p)


@pytest.fixture(params=[i for i in range(0, 24)])
# Iterate once for every hour in the day
def hours(request):
    return request.param


@pytest.fixture(params=[True, False])
# Toggle TZ settings
def tz_settings(request):
    return request.param


@pytest.mark.django_db
def test_no_config(client):
    # *Don't* use config fixture to *avoid* setting up the Config object.
    # Accessing any page without having set up a Config object should throw an exception.
    with pytest.raises(AttributeError) as excinfo:
        url = reverse("tangerine:home")
        client.get(url)
    assert "AttributeError" in str(excinfo)


@pytest.mark.django_db
def test_good_slug_good_view(config, post1, client):
    url = post1.get_absolute_url()
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_bad_slug_404(config, client):
    url = reverse(
        "tangerine:post_detail", kwargs={"year": 2002, "month": 7, "day": 23, "slug": "whatever"}
    )
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_all_hours_in_24(config, client, settings, hours, tz_settings):
    """
    Use parameterized fixtures to test posts made in all 24 hours in a day, ensuring that URL still resolves
    whether host project is TZ aware or not (test both with `USE_TZ = True` and `USE_TZ = False`).
    We want to prove that we don't slip over the date boundary no matter what time of day we post,
    thus changing the URL and generating 404s. We want to test not just that all date URLs resolve,
    but that all 24 URLs are identical. Due to paramaterization, this test runs itself 48 times!
    """

    # First two statements use parameterized fixtures (tz_settings and hours)
    settings.USE_TZ = tz_settings
    ref_pub_date = datetime.datetime.strptime(
        "{} {} {} {} {} {}".format(2018, 2, 2, hours, 3, 3), "%Y %m %d %H %M %S"
    )

    hourly_post = PostFactory(slug="somepost", pub_date=make_aware(ref_pub_date))
    assert "2018/2/2" in hourly_post.get_absolute_url()
    url = hourly_post.get_absolute_url()
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_top_level_comment_no_auth(config, comment_data, post1, client):
    # Comment threading is initiated in templates, so we don't have unit tests for threaded comment posting - just this.
    # For unauthenticated users, we store the name and email.
    url = post1.get_absolute_url()
    response = client.post(url, data=comment_data)
    assert response.status_code == 302  # Redirect to the same view

    # Below doesn't mean comment is approved, just that it exists with correct data
    new_comment = Comment.objects.filter(post=post1).first()
    assert new_comment.name == comment_data.get("name")[0]
    assert new_comment.email == comment_data.get("email")[0]
    assert new_comment.website == comment_data.get("website")[0]
    assert new_comment.body == comment_data.get("body")[0]


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
    new_comment_data["parent_id"] = parent_id
    new_comment_data["body"] = "xyz"

    # Post child comment, then get both back from the db. Expected child/parent relation is preserved.
    admin_client.post(url, data=new_comment_data)
    orig_comment = Comment.objects.get(id=parent_id)
    child_comment = orig_comment.child_comments().first()
    assert child_comment.parent.id == orig_comment.id
    assert child_comment.body == "xyz"


@pytest.mark.smoketest
@pytest.mark.django_db
def test_tag_view(config, client):
    p = PostFactory()
    p.tags.add("python")

    # Access with a good tag, then with a bad tag
    url = reverse("tangerine:tag", kwargs={"tag_slug": "python"})
    response = client.get(url)
    assert response.status_code == 200

    url = reverse("tangerine:tag", kwargs={"tag_slug": "frisbee"})
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.smoketest
@pytest.mark.django_db
def access_comment_management(config, posts_with_comments, admin_client, client):
    url = reverse("tangerine:manage_comments")

    # With admin auth
    response = admin_client.get(url)
    assert response.status_code == 200

    # With no auth
    response = client.get(url)
    assert response.status_code == 302
