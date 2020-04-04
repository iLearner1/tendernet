# lots/views.py


from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from .filters import ArticleFilter
from .models import Article
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
import datetime

def post_list(request):
    posts = Article.objects.order_by('-created')



    myFilter = ArticleFilter(request.GET, queryset=Article.objects.all())
    posts = myFilter.qs

    query = request.GET.get('q')
    if query:
        posts = Article.objects.filter(
            Q(title__icontains=query) |
            Q(body__icontains=query)
        )


    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    if page is None:
        start_index = 0
        end_index = 7
    else:
        (start_index, end_index) = proper_pagination(posts, index=4)

    page_range = list(paginator.page_range)[start_index:end_index]

    context = {
        'posts': posts,
        'myFilter': myFilter,
        



    }

    return render(request, 'article_list.html', context)


def proper_pagination(posts, index):
    start_index = 0
    end_index = 7
    if posts.number > index:
        start_index = posts.number - index
        end_index = start_index + end_index
    return (start_index, end_index)


def post_detail(request, id, slug,):
    post = get_object_or_404(Article, id=id, slug=slug)


    dat6 = datetime.timedelta(days=5)
    dat3 = post.date
    dat7 = dat3 - dat6
    dat4 = post.date - datetime.datetime.now(timezone.utc)

    
    


    is_favourite = False
    if post.favourite.filter(id=request.user.id).exists():
        is_favourite = True

    context = {
        'post': post,
        'is_favourite': is_favourite,
        'dat3':dat3,
        'dat4': dat4,
    }

    return render(request, "article_detail.html", context)


def post_favourite_list(request):
    user = request.user
    favourite_posts = user.favourite.all()
    context = {
        'favourite_posts': favourite_posts,
    }
    return render(request, 'post_favourite_list.html', context)


def favourite_post(request, slug):
    post = get_object_or_404(Article, slug=slug)
    if post.favourite.filter(id=request.user.id).exists():
        post.favourite.remove(request.user)
    else:
        post.favourite.add(request.user)
    return HttpResponseRedirect(post.get_absolute_url())
