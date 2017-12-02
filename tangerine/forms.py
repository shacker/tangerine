from django import forms
from tangerine.models import Comment


class CommentForm(forms.ModelForm):
    name = forms.CharField(
        label="Name",
        required=True,
    )
    email = forms.EmailField(
        label="Email",
        required=True,
    )

    class Meta:
        model = Comment
        fields = ['name', 'email', 'website', 'body']
        # Hiddent parent_id field inserted manually in form template


class CommentSearchForm(forms.Form):
    q = forms.CharField(label='Search term', max_length=100)
