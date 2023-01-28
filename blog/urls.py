from django.urls import path
from blog import views

urlpatterns = [
    path('', views.PostList.as_view(), name='blog'),
    path('<slug:slug>/<int:pk>/', views.PostDetail.as_view(), name='post_detail'),
    path('like/<slug:slug>/<int:pk>/', views.PostLike.as_view(), name='post_like'),
]
