from django.urls import path
from .views import *

app_name = 'posts'

urlpatterns = [
    path('feed/', post_comment_create_and_list_view_feed, name='feed-posts-view'),
    path('all/', post_comment_create_and_list_view_all, name='all-post-view'),
    path('liked/', like_unlike, name='like-post-view'),
    path('id/<pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('id/<pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('id/<pk>/', post_detail, name='post-detail'),

]
