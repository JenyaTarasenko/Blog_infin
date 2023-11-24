from django.urls import path
from . import views


app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post_list'),#главная страничка 'blog'
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tags'),#путь для тэгов постов
    # path('post/<int:id>/', views.post_detail, name='post_detail'),#детальная информация поста
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name='post_detail'),
    path('<int:post_id>/', views.post_comment, name='post_comment'),
]