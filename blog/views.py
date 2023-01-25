from django.shortcuts import render, get_object_or_404, reverse
from django.views import generic, View
from django.http import HttpResponseRedirect
from .models import Post
from .forms import CommentForm


class PostList(generic.ListView):

    model = Post
    queryset = Post.objects.order_by('-created_on')
    template_name = 'blog/blog.html'

class PostDetail(View):

    def get(self, request, slug, pk, *args, **kwargs):

        queryset = Post.objects.all()
        post = get_object_or_404(queryset,slug=slug, pk=pk)
        comments = post.comments.order_by('-created_on')
        liked = False
        if post.likes.filter(id=self.request.user.id).exists():
            liked = True

        return render(
            request,
            'blog/post_detail.html',
            {
                'post': post,
                'comments': comments,
                'commented': False,
                'liked': liked,
                'comment_form': CommentForm()
            },
        )

    def post(self, request, slug, pk, *args, **kwargs):

        if request.user.is_authenticated:
            queryset = Post.objects.all()
            post = get_object_or_404(queryset, slug=slug, pk=pk)
            comment_form = CommentForm(data=request.POST)

            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()

        return HttpResponseRedirect(reverse('post_detail', args=[slug, pk]))
