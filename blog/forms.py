from django import forms
from django_summernote.widgets import SummernoteInplaceWidget
from .models import Post, Comment
from .widgets import CustomClearableFileInput

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('body',)

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['body'].label = ''
        self.fields['body'].widget.attrs['placeholder'] = 'Kommentar...'


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

    featured_image = forms.ImageField(label='Image', required=True, widget=CustomClearableFileInput)

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['title'].label = 'Namn post'
        self.fields['title'].widget.attrs['placeholder'] = 'Titel...'
        self.fields['featured_image'].label = 'Omslagsbild'
        self.fields['title'].widget.attrs['placeholder'] = 'Titel...'
        self.fields['content'].label = ''
