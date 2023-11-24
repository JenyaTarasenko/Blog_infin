from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from taggit.managers import TaggableManager #модель теггирования


class PublishedManger(models.Manager):
    """
    Возвращает набор  QuerySet фильтрующий посты по их статусу  PUBLISHED.
    """
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class Post(models.Model):
    """
    Пост
    """
    class Status(models.TextChoices):
        """
        подклассирование класса models.TextChoices
        "статус поста"
        """
        DRAFT = 'DF', 'DRAFT'
        PUBLISHED = 'PB', 'Published'

    tags = TaggableManager()  # создание менеджераа
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250,
                            unique_for_date='publish')# 'unique_for_date='publish' используется для поиск оптимизации
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='blog_posts')
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2,
                              choices=Status.choices,
                              default=Status.DRAFT)
    objects = models.Manager()#менеджер применяемый по умолчанию
    published = PublishedManger()# конкретно прикладной менеджер


    class Meta:
        ordering = ['-publish']#перебирает поля публикации с конца
        indexes = [
            models.Index(fields=['-publish']),#дляиндексации
        ]

    def __str__(self):
        return self.title


    def get_absolute_url(self):# ссылка на  'post_detail'
        # return reverse('blog:post_detail', args=[self.id])
        return reverse('blog:post_detail',
                       args=[self.publish.year,
                             self.publish.month,
                             self.publish.day,
                             self.slug]
                       )


class Comment(models.Model):
    """
    модель коментарие связанная с постами
    каждый пост содержит несколько коментариев
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['created']),
        ]

    def __str__(self):
        return f'Comment by {self.name} on {self.post}'



