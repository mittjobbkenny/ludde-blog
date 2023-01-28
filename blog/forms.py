from django import forms
from .models import Post, Comment

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('body',)
    
    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['body'].label = ''
        self.fields['body'].widget.attrs['placeholder'] = 'Skriv en kommentar...'


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = [
            'title',
            'featured_image',
            'content'
        ]
