from blog.models import Category, Comment, Post, User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import BlogForm, CommentForm, UserForm


def post_query():
    """Фильтрует объект Post"""
    return Post.objects.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    )


class BlogListView(ListView):
    """Выводит главную страницу index.html (список постов)"""
    model = Post
    template_name = 'blog/index.html'
    query = post_query().select_related(
        'category',
        'location',
        'author'
    )
    queryset = query.annotate(comment_count=Count('comment', distinct=True))

    paginate_by = 10


class PostDetailView(DetailView):
    """Выводит детальную информацию о посте"""
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        """Переопределяем get_context_data для расширения context"""
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comment.select_related('author')
        )
        return context


class СategoryListView(ListView):
    """Выводит страницу категорий"""
    model = Post
    template_name = 'blog/category.html'
    query = post_query().select_related(
        'category',
        'location',
        'author'
    )
    queryset = query.annotate(comment_count=Count('comment', distinct=True))
    paginate_by = 10

    def get_context_data(self, **kwargs):
        """Переопределяем get_context_data для расширения context"""
        context = super().get_context_data(**kwargs)
        category = get_object_or_404(Category.objects.values(
            'id',
            'title',
            'description'
        ).filter(
            is_published=True
        ), slug=self.kwargs['category_slug']
        )
        context['category'] = category
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание новой публикации"""
    model = Post
    form_class = BlogForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        """Переопределяем form_valid для добавления author"""
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    """Редактируем публикацию"""
    model = Post
    form_class = BlogForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        """Переопределяем dispatch для проверки авторства"""
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != request.user:
            return redirect('blog:post_detail', kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self, **kwargs):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['pk']}
            )


class PostDeleteView(LoginRequiredMixin, DeleteView):
    """Удаляем публикацию"""
    login_url = 'blog:index'
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        """Переопределяем dispatch для проверки авторства"""
        get_object_or_404(Post, pk=kwargs['pk'], author=request.user)
        return super().dispatch(request, *args, **kwargs)


class ProfileListView(ListView):
    """Выводит страницу категорий"""
    model = Post
    template_name = 'blog/profile.html'
    context_object_name = 'page_obj'
    pk_url_kwarg = 'name'
    paginate_by = 10

    def get_queryset(self):
        query = Post.objects.select_related(
            'category',
            'location',
            'author'
        ).filter(
            author__username=self.kwargs['name'],
        )
        queryset = query.annotate(
            comment_count=Count('comment', distinct=True)
            )
        return queryset

    def get_context_data(self, **kwargs):
        """Переопределяем get_context_data для расширения context"""
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(
            User.objects.all(),
            username=self.kwargs['name']
        )
        context['profile'] = profile
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактируем профиль"""
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        username = self.request.user.username
        return reverse("blog:profile", kwargs={"username": username})


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание нового комментария"""
    post1 = None
    model = Comment
    form_class = CommentForm
    template_name = 'blog/detail.html'

    def dispatch(self, request, *args, **kwargs):
        self.post1 = get_object_or_404(Post, id=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post1
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'pk': self.request.user.id}
            )


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    """Редактируем комментария"""
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        """Переопределяем dispatch для проверки авторства"""
        get_object_or_404(Comment,
                          pk=kwargs['comment_id'],
                          author=request.user
                          )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Переопределяем get_context_data для расширения context"""
        context = super().get_context_data(**kwargs)
        context['post'] = Post.objects.get(pk=self.kwargs['post_id'])
        return context

    def get_success_url(self, **kwargs):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['post_id']}
            )


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    """Удаляем комментарий"""
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        """Переопределяем dispatch для проверки авторства"""
        get_object_or_404(Comment,
                          pk=kwargs['comment_id'],
                          author=request.user
                          )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self, **kwargs):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['post_id']}
            )
