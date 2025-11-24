"""blogdiary URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.PostsListView.as_view(), name="index"),
    path("posts/<int:pk>/", views.PostDetailView.as_view(), name="post_detail"),
    path("posts/<int:pk>/edit/", views.EditPostView.as_view(), name="edit_post"),
    path("posts/<int:pk>/delete/", views.DeletePostView.as_view(), name="delete_post"),
    path("posts/<int:post_id>/comment/", views.CommentPostView.as_view(), name="add_comment"),
    path(
        "posts/<int:post_id>/edit_comment/<int:comment_id>/",
        views.EditCommentView.as_view(),
        name="edit_comment",
    ),
    path(
        "posts/<int:post_id>/delete_comment/<int:comment_id>/",
        views.DeleteCommentView.as_view(),
        name="delete_comment",
    ),
    path("posts/create/", views.CreatePostView.as_view(), name="create_post"),
    path(
        "category/<slug:category_slug>/",
        views.CategoryPostsListView.as_view(),
        name="category_posts",
    ),
    path("profile/edit/", views.EditProfileView.as_view(), name="edit_profile"),
    path("profile/<slug:username>/", views.UserProfileView.as_view(), name="profile"),
]
