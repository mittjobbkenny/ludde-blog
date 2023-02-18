from django.shortcuts import render, get_object_or_404, reverse
from django.contrib import messages
from django.views import generic, View
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import FormMixin
from .models import Post, Comment
from .forms import PostForm, CommentForm


class PostList(generic.ListView):

    model = Post
    template_name = 'blog/blog.html'
    paginate_by = 6

    def get_queryset(self):
        posts_all = Post.objects.all()
        sort_by = self.request.GET.get('sort')
        if sort_by == 'desc':
            posts_all = posts_all.order_by('-created_on')
        elif sort_by == 'asc':
            posts_all = posts_all.order_by('created_on')
        else:
            posts_all = posts_all.order_by('-created_on')
        return posts_all

    def get_context_data(self, **kwargs):
        context = super(PostList, self).get_context_data(**kwargs)
        context['num_posts'] = Post.objects.all().count()

        display_thumb = self.request.GET.get('thumb')
        if display_thumb == 'list':
            context['thumb'] = 'list'
        else:
            context['thumb'] = 'grid'

        sort_by = self.request.GET.get('sort')
        if sort_by:
            context['sort_by'] = sort_by
        else:
            context['sort_by'] = 'desc'

        return context


class PostDetail(FormMixin, generic.DetailView):

    model = Post
    template_name = 'blog/post_detail.html'
    form_class = CommentForm

    def get_success_url(self):
        return reverse('post_detail', kwargs={'slug': self.object.slug, 'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super(PostDetail, self).get_context_data(**kwargs)
        context['comments'] = self.object.comments.order_by('-created_on')
        context['liked'] = self.object.likes.filter(id=self.request.user.id).exists()
        context['commented'] = self.object.comments.filter(author=self.request.user.id).exists()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if request.user.is_authenticated:
            if form.is_valid():
                comment = form.save(commit=False)
                comment.post = self.object
                comment.author = request.user
                return self.form_valid(form)
            else:
                messages.info(self.request, 'Ingen kommentar')
                return self.form_invalid(form)

    def form_valid(self, form):
        form.save()
        messages.info(self.request, 'Kommentar tillagd')
        return super(PostDetail, self).form_valid(form)


class PostLike(LoginRequiredMixin, View):
  
    def post(self, request, slug, pk, *args, **kwargs):
        post = get_object_or_404(Post, slug=slug, pk=pk)
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
            messages.info(self.request, 'Gilla borttagen')
        else:
            post.likes.add(request.user)
            messages.info(self.request, 'Gilla tillagd')

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
