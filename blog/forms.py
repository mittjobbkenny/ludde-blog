from django import forms
from django_summernote.widgets import SummernoteInplaceWidget
from .models import Post, Comment

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('body',)
        widgets = {
            'body': SummernoteInplaceWidget(),
        }

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['body'].label = ''


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = [
            'title',
            'featured_image',
            'content'
        ]
        widgets = {
            'content': SummernoteInplaceWidget(),
        }

    def __init__(self, *args, **kwargs):
            super(PostForm, self).__init__(*args, **kwargs)
            self.fields['title'].label = 'Ny post'
            self.fields['title'].widget.attrs['placeholder'] = 'Titel...'
            self.fields['featured_image'].label = 'Omslagsbild'
            self.fields['title'].widget.attrs['placeholder'] = 'Titel...'
            self.fields['content'].label = ''
