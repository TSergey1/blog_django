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


def post_annotate(query):
    """Подсчет комментариев"""
    return query.annotate(
        comment_count=Count('comment')
    ).order_by('-pub_date')


class PostMixin:
    """PostMixin"""
    model = Post
    form_class = BlogForm
    template_name = 'blog/create.html'


class CommentMixin:
    """Mixin"""
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'


class CommentDefMixin:
    """DefMixin"""
    def dispatch(self, request, *args, **kwargs):
        """Переопределяем dispatch для проверки авторства"""
        get_object_or_404(Comment,
                          pk=kwargs['comment_id'])
        if self.get_object().author != request.user:
            return redirect('blog:post_detail', pk=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self, **kwargs):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'pk': self.kwargs['post_id']}
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
    queryset = post_annotate(query)
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


class CategoryListView(ListView):
    """Выводит страницу категорий"""
    model = Post
    template_name = 'blog/category.html'
    paginate_by = 10

    def get_queryset(self):
        query = Post.objects.select_related(
            'category',
            'location',
            'author'
        ).filter(
            category__slug=self.kwargs['category_slug'],
            pub_date__lte=timezone.now(),
            is_published=True,
        )
        return post_annotate(query)

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


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):
    """Создание новой публикации"""

    def form_valid(self, form):
        """Переопределяем form_valid для добавления author"""
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, PostMixin, UpdateView):
    """Редактируем публикацию"""

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
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        """Переопределяем dispatch для проверки авторства"""
        instance = get_object_or_404(Post, pk=kwargs['pk'])
        if instance.author != request.user:
            return redirect('blog:index')
        return super().dispatch(request, *args, **kwargs)


class ProfileListView(ListView):
    """Выводит страницу категорий"""
    model = Post
    template_name = 'blog/profile.html'
    slug_url_kwarg = 'name'
    paginate_by = 10

    def get_queryset(self):
        if self.request.user.username == self.kwargs['name']:
            query = Post.objects.select_related(
                'category',
                'location',
                'author'
            ).filter(
                author__username=self.kwargs['name'],
            )
        else:
            query = post_query().select_related(
                'category',
                'location',
                'author'
            ).filter(
                author__username=self.kwargs['name'],
            )
        return post_annotate(query)

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
        return reverse("blog:profile", kwargs={"name": username})


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание нового комментария"""
    post_ = None
    model = Comment
    form_class = CommentForm
    template_name = 'blog/detail.html'

    def dispatch(self, request, *args, **kwargs):
        self.post_ = get_object_or_404(Post, id=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'pk': self.kwargs['pk']}
        )


class CommentUpdateView(LoginRequiredMixin,
                        CommentMixin,
                        CommentDefMixin,
                        UpdateView):
    """Редактируем комментария"""
    form_class = CommentForm

    def get_context_data(self, **kwargs):
        """Переопределяем get_context_data для расширения context"""
        context = super().get_context_data(**kwargs)
        context['post'] = Post.objects.get(pk=self.kwargs['post_id'])
        return context


class CommentDeleteView(LoginRequiredMixin,
                        CommentMixin,
                        CommentDefMixin,
                        DeleteView):
    """Удаляем комментарий"""
    pass
