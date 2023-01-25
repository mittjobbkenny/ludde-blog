from django.shortcuts import render
from django.views import generic
from .models import Post, Comment


class PostList(generic.ListView):

    model = Post
    queryset = Post.objects.order_by('-created_on')
    template_name = 'blog/blog.html'
