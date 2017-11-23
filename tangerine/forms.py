from django.forms import ModelForm
from tangerine.models import Comment


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'website', 'body']
        # Hiddent parent_id field inserted manually in form template
