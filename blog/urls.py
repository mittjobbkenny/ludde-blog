from django.urls import path
from blog import views

urlpatterns = [
    path('', views.PostList.as_view(), name='blog'),
    path('<slug:slug>/<int:pk>/', views.PostDetail.as_view(), name='post_detail'),
    path('like/<slug:slug>/<int:pk>/', views.PostLike.as_view(), name='post_like'),
    path('add/', views.PostAdd.as_view(), name='post_add'),
    path('update/<slug:slug>/<int:pk>/', views.PostUpdate.as_view(), name='post_update'),
    path('delete/<slug:slug>/<int:pk>/', views.PostDelete.as_view(), name='post_delete'),
    path('comment-delete/<slug:slug>/<int:pk>/', views.CommentDelete.as_view(), name='comment_delete'),
    path('comment-update/<slug:slug>/<int:pk>/', views.CommentUpdate.as_view(), name='comment_update'),
    path('search/', views.SearchResults.as_view(), name='search_results'),
]
