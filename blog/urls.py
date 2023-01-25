from django.urls import path
from blog import views

urlpatterns = [
    path('', views.PostList.as_view(), name='blog'),
]
