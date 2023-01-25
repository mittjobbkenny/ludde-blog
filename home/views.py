from django.views import generic
from blog .models import Post


class Home(generic.ListView):

    model = Post
    queryset = Post.objects.order_by('-created_on')
    template_name = 'home/index.html'
