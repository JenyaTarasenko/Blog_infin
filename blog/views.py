from django.shortcuts import render, get_object_or_404
from .models import Post,Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger #если параметр страницы не числа
from .forms import EmailPostForm, CommentForm
from django.views.decorators.http import require_POST
from taggit.models import Tag  # теги
from django.db.models import Count    # агрегирование подсчет  тегов







def post_list(request, tag_slug=None):
    """
    главная со всеми новостями
    """
    post_list = Post.objects.all()
    #конструкция теггирования начало
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])# __in поиск по полю
    # конструкция теггирования  конец
    #постраничная разбивка с 3 поста на странице
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # если ну целое число то выдает первую страницу
        posts = paginator.page(1)
    except EmptyPage:
        # если page_number вне диапазона
        # выдать последнюю страницу
        posts = paginator.page(paginator.num_pages)
    return render(request,
                  'blog/post/list.html',
                  {'posts': posts, 'tag':tag}
                  )



def post_detail(request, year, month, day, post):
    """
    Детальная информация поста, вытягивает id
    если нет поста выводит исключение
    """
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,#забирает слаг год месяц день и вывод в url
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    # извлекаем все активные коментарии к посту
    comments = post.comments.filter(active=True)
    #форма для коментариев пользователя
    form = CommentForm()
    # список схожих постов
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    return render(request, 'blog/post/detail.html', {'post': post,
                                                     'comments': comments, 'form': form, 'similar_posts': similar_posts})


def post_share(request, post_id):
    """
    форма
    """
    # извлекаем пост по идентификатору
    post = get_object_or_404(Post,
                             id=post_id,
                             status=Post.Status.PUBLISHED)
    if request.metgod =='POST':
        # форма была передана на обработку
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # поля формы успешно прошли валидацию
            cd = form.cleaned_data
            # отправить электронное писмо
    else:
        form = EmailPostForm
    return render(request,'blog/post/share.html',
                  {'post': post, 'form': form})



@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        #создается обьект не сохраняя в базе данных
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    return  render(request, 'blog/post/comment.html', {'post': post,
                                                       'form': form, 'comment': comment})