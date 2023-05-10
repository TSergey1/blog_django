from django.shortcuts import get_object_or_404, render, redirect
from blog.models import Post, Category, Comment, User
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import BlogForm, CommentForm, UserForm
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Count


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
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        """Переопределяем dispatch для проверки авторства"""
        get_object_or_404(Post, pk=kwargs['pk'], author=request.user)
        return super().dispatch(request, *args, **kwargs)


def profile(request, name):
    """Выводит профиль пользователя"""
    template = 'blog/profile.html'
    profile = get_object_or_404(User.objects.all(), username=name)
    query = Post.objects.select_related(
        'category',
        'location',
        'author'
    ).filter(
        author__username=name,
    )
    posts_user = query.annotate(comment_count=Count('comment', distinct=True))
    paginator = Paginator(posts_user, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj, 'profile': profile}
    return render(request, template, context)


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


# class CommentCreateView(LoginRequiredMixin, CreateView):
#     """Создание нового комментария"""
#     post = None
#     model = Comment
#     form_class = CommentForm
#     template_name = 'blog/detail.html'

#     def dispatch(self, request, *args, **kwargs):
#         self.post = get_object_or_404(Post, pk=kwargs['pk'])
#         return super().dispatch(request, *args, **kwargs)

#     def form_valid(self, form):
#         form.instance.author = self.request.user
#         form.instance.post = self.post
#         return super().form_valid(form)

#     def get_success_url(self):
#         return reverse_lazy(
#             'blog:post_detail', kwargs={'pk': self.request.user.id}
#             )


@login_required
def add_comment(request, pk):
    """Создание нового комментария"""
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', pk=pk)


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    """Редактируем комментария"""
    model = Comment
    form_class = CommentForm
    # template_name = 'blog/detail.html'
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
