from django.shortcuts import render, get_object_or_404, reverse
from django.contrib import messages
from django.views import generic, View
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Post, Comment
from .forms import PostForm, CommentForm


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
        commented = False
        if request.user.is_authenticated:
            if comments.filter(author=self.request.user).exists():
                commented = True

        return render(
            request,
            'blog/post_detail.html',
            {
                'post': post,
                'comments': comments,
                'commented': commented,
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
                messages.info(request, 'Kommentar tillagd')

        return HttpResponseRedirect(reverse('post_detail', args=[slug, pk]))


class PostLike(LoginRequiredMixin, View):
  
    def post(self, request, slug, pk, *args, **kwargs):

        post = get_object_or_404(Post, slug=slug, pk=pk)
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)

        return HttpResponseRedirect(reverse('post_detail', args=[slug, pk]))


class PostAdd(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):

    model = Post
    template_name = 'blog/post_add.html'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_superuser


class CommentDelete(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):

    model = Comment
    template_name = 'blog/post_detail.html'

    def get_success_url(self):
        post = Post.objects.get(pk=self.object.post.pk)
        messages.info(self.request, 'Kommentar borttagen')
        return post.get_absolute_url()

    def test_func(self):
        comment = self.get_object()
        if self.request.user == comment.author:
            return True
        return False
