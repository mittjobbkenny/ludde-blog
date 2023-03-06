from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import generic, View
from django.http import Http404
from django.db.models import Q
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
        sort_com = self.request.GET.get('sort_com')
        if sort_com == 'asc_com':
            context['comments'] = self.object.comments.order_by('created_on')
            context['asc_com'] = 'asc_com'
        else:
            context['comments'] = self.object.comments.order_by('-created_on')
            context['desc_com'] = 'desc_com'
        context['update_form'] = CommentForm()
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
        messages.info(self.request, 'Post tillagd')
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_superuser


class PostUpdate(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):

    model = Post
    template_name = 'blog/post_update.html'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.info(self.request, 'Post uppdaterad')
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDelete(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):

    model = Post
    template_name = 'post_detail.html'
    success_url = reverse_lazy('blog')

    def form_valid(self, form):
        messages.info(self.request, 'Post borttagen')
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


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


class CommentUpdate(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):

    model = Comment
    template_name = 'blog/post_detail.html'
    form_class = CommentForm

    def get_success_url(self):
        post = Post.objects.get(pk=self.object.post.pk)
        return post.get_absolute_url()

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.info(self.request, 'Kommentar uppdaterad')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.info(self.request, 'Kommentar ej uppdaterad')
        return HttpResponseRedirect(self.get_success_url())

    def test_func(self):
        comment = self.get_object()
        if self.request.user == comment.author:
            return True
        return False


class SearchResults(generic.ListView):

    model = Post
    template_name = 'blog/search_results.html'
    allow_empty = False
    paginate_by = 6

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            object_list = Post.objects.filter(Q(title__icontains=query))
            if not object_list:
                messages.info(self.request, 'Inga träffar')
                object_list = query
                return object_list
            sort_by = self.request.GET.get('sort')
            if sort_by == 'desc':
                object_list = object_list.order_by('-created_on')
            elif sort_by == 'asc':
                object_list = object_list.order_by('created_on')
            else:
                object_list = object_list.order_by('-created_on')
            return object_list

    def get_context_data(self, **kwargs):
        context = super(SearchResults, self).get_context_data(**kwargs)
        context['post_search'] = self.request.GET.get('q')
        query = self.request.GET.get('q')
        context['num_search'] = Post.objects.filter(Q(title__icontains=query)).count()
        context['recent_posts'] = Post.objects.order_by('-created_on')[:3]

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

    def dispatch(self, *args, **kwargs):
        try:
            return super().dispatch(*args, **kwargs)
        except Http404:
            messages.info(self.request, 'Sökfältet är tomt')
            return redirect('blog')
