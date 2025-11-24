from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import CommentForm, EditUserForm, PostForm
from .models import Category, Post, PostComments

current_time = timezone.now()

User = get_user_model()

OBJ_ON_PAGE = 10


class ListPostsMixin:
    """Миксин для списка постов с оптимизацией запросов"""

    model = Post
    paginate_by = OBJ_ON_PAGE

    def get_base_queryset(self):
        """Базовый QuerySet с аннотациями и select_related"""
        return (
            Post.objects.select_related("author", "category", "location")
            # аннотация добавляет comment_count по related_name comments, с маленьким фильтром
            .annotate(comment_count=Count("comments", comments__is_published=True)).order_by(
                "-pub_date", "title"
            )
        )

    def get_filtered_queryset_date_pub(self, queryset):
        return queryset.filter(
            pub_date__lte=current_time,
            is_published=True,
            category__is_published=True,
        )


class CategoryPostsListView(ListPostsMixin, ListView):
    template_name = "blog/category.html"

    def get_queryset(self):
        category_slug = self.kwargs["category_slug"]
        self.category = get_object_or_404(
            Category, slug=self.kwargs["category_slug"], is_published=True
        )
        return self.get_filtered_queryset_date_pub(self.get_base_queryset()).filter(
            category__slug=category_slug,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


class UserProfileView(ListPostsMixin, ListView):
    template_name = "blog/profile.html"
    slug_field = "username"  # CBV ищет это поле в моделе User
    slug_url_kwarg = "username"  # имя параметра из URL

    def get_queryset(self):
        username = self.kwargs.get(self.slug_url_kwarg)
        self.profile_user = get_object_or_404(
            User.objects.only("id"), **{self.slug_field: username}
        )

        # базовая фильтрация по пользователю
        queryset = self.get_base_queryset().filter(author=self.profile_user)

        # если текущий пользователь НЕ владелец профиля - примениьб фильтры
        if self.request.user != self.profile_user:
            queryset = self.get_filtered_queryset_date_pub(queryset)
        return queryset

    # добавить в контекст все по пользователю
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["profile"] = self.profile_user
        # флаг, является ли текущий пользователь владельцем профиля, не испльзуется пока что
        context["is_owner"] = self.request.user == self.profile_user
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = EditUserForm
    template_name = "blog/user.html"

    def get_object(self, queryset=None):
        return self.request.user


class PostsListView(ListPostsMixin, ListView):
    template_name = "blog/index.html"

    def get_queryset(self):
        return self.get_filtered_queryset_date_pub(self.get_base_queryset())


class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"

    # при создании присваивоить пользователя
    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostOwnerCkeckMixin:
    """
    Примиксовать для проверки владелец ли пользователь у поста, нужно
    для редактирования или удаления. Если нет, редирект на сам пост.
    """

    model = Post
    template_name = "blog/create.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("blog:post_detail", pk=kwargs["pk"])

        # Проверяем, что пользователь - автор поста
        post = get_object_or_404(Post, pk=kwargs["pk"])
        if post.author != request.user:
            return redirect("blog:post_detail", pk=kwargs["pk"])

        return super().dispatch(request, *args, **kwargs)


class PostDetailView(DetailView):
    model = Post
    # template_name = "blog/post_detail.html" # не нужно т.к. имя ожидаемое

    def get_queryset(self):
        # базовый queryset с оптимизацией связанных моделей
        queryset = Post.objects.select_related("category", "location", "author")

        # если пользователь - автор поста, показываем без ограничений
        # проверяем это в get_object, а здесь просто возвращаем все посты
        return queryset

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        pk = self.kwargs.get("pk")
        post = get_object_or_404(queryset, pk=pk)

        # проверка доступ
        if post.author == self.request.user:
            # автор видит всё
            return post
        else:
            # не-авторы видят только опубликованное
            if post.pub_date <= current_time and post.is_published and post.category.is_published:
                return post
            else:
                raise Http404

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        context["comments"] = (
            # Дополнительно подгружаем авторов комментариев,
            # чтобы избежать множества запросов к БД.
            self.object.comments.select_related("author")
        )
        return context


class EditPostView(PostOwnerCkeckMixin, LoginRequiredMixin, UpdateView):
    form_class = PostForm

    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"pk": self.object.id})


class DeletePostView(PostOwnerCkeckMixin, LoginRequiredMixin, DeleteView):

    def get_success_url(self):
        return reverse("blog:index")


class CommentMixin(LoginRequiredMixin):
    post_o = None
    model = PostComments
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.post_o = get_object_or_404(Post, pk=kwargs["post_id"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_o
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("blog:post_detail", kwargs={"pk": self.post_o.id})


class CommentDelEdMixin(CommentMixin):
    template_name = "blog/comment.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment"] = self.get_object()
        return context

    def get_object(self):
        # Получаем комментарий и проверяем авторизацию
        return get_object_or_404(
            PostComments,
            pk=self.kwargs["comment_id"],
            author=self.request.user,  # проверка, что автор - текущий пользователь
        )


class CommentPostView(CommentMixin, CreateView):
    template_name = "blog/detail.html"


class EditCommentView(CommentDelEdMixin, UpdateView):
    pass


class DeleteCommentView(CommentDelEdMixin, DeleteView):
    pass
