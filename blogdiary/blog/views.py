from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import Category, Post

current_time = timezone.now()


def get_post_list():
    # используется для index и all_posts
    post_list = Post.objects.select_related(
        "category",
        "location",
        "author",
    ).filter(
        pub_date__lte=current_time,
        is_published=True,
        category__is_published=True,
    )
    return post_list


def index(request):
    template = "blog/index.html"
    post_list = get_post_list()[:5]
    content = {"post_list": post_list}
    return render(request, template, content)


def all_posts(request):
    template = "blog/index.html"
    post_list = get_post_list()  # .order_by("category__title")
    content = {"post_list": post_list}
    return render(request, template, content)


def post_detail(request, id):
    template = "blog/detail.html"
    post_info = get_object_or_404(
        Post.objects.select_related(
            "category",
            "location",
            "author",
        ).filter(
            pk=id,
            pub_date__lte=current_time,
            is_published=True,
            category__is_published=True,
        )
    )
    content = {"post": post_info}
    return render(request, template, content)


def category_posts(request, category_slug):
    template = "blog/category.html"
    post_list = Post.objects.select_related(
        "category",
        "location",
        "author",
    ).filter(
        pub_date__lte=current_time,
        is_published=True,
        category__is_published=True,
        category__slug=category_slug,
    )
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )
    content = {"post_list": post_list, "category": category}
    return render(request, template, content)
