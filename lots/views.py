# lots/views.py
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .filters import ArticleFilter
from .models import Article, FavoriteSearch, Cities
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
import datetime
import json
from lots.utils.Choices import ZAKUP_CHOICES, PURCHASE_CHOICES


def post_list(request):

    print("request type")
    print(request.method)

    request_object = request.GET
    title_q = Q()

    if request.method == "POST":
        request_object = request.POST

        if 'title' in request.POST:
            if request.POST.get('title'):
                title_tokens = request.POST.get('title').split()
                for keyword in title_tokens:
                    title_q |= Q(title__contains=keyword)

    print("req object")
    print(request_object.items())

    cities = request_object.getlist("city[]")
    purchase_method = request_object.getlist("purchase_method[]")
    statzakup = request_object.getlist("statzakup[]")

    q = Q()
    q &= Q(date__gte=timezone.now())

    myFilter = {}

    if request.method == "POST":
        q &= title_q
        myFilter['title'] = request.POST.get('title')

    posts = Article.objects.filter(q)

    print("posts")
    print(posts)
    print(len(posts))

    myFilter = {}

    # dict compression
    filters = {
        k: v
        for (k, v) in request_object.items()
        if k != "city[]" or k != "purchase_method[]" or k != "statzakup[]"
    }
    print("filters")
    print(filters)

    if cities or purchase_method or statzakup:
        print("if cities or purchase_method or statzakup:")
        posts = Article.objects.filter(
            Q(city__id__in=cities)
            | Q(statzakup__in=statzakup)
            | Q(purchase_method__in=purchase_method)
        )
        myFilter = ArticleFilter(filters, queryset=posts)
        posts = myFilter.qs

    cities = Cities.objects.all()

    paginator = Paginator(posts, 10)
    page = request_object.get("page", 1)

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
        "posts": posts,
        "myFilter": myFilter,
        "cities": cities,
        "ZAKUP_CHOICES": ZAKUP_CHOICES,
        "PURCHASE_CHOICES": PURCHASE_CHOICES,
    }

    return render(request, "article_list.html", context)


def proper_pagination(posts, index):
    start_index = 0
    end_index = 7
    if posts.number > index:
        start_index = posts.number - index
        end_index = start_index + end_index
    return (start_index, end_index)


def post_detail(request, id, slug):
    post = get_object_or_404(Article, id=id, slug=slug)
    dat6 = datetime.timedelta(days=5)
    dat3 = post.date
    dat7 = dat3 - dat6
    dat4 = post.date - datetime.datetime.now(timezone.utc)

    is_favourite = False
    if post.favourite.filter(id=request.user.id).exists():
        is_favourite = True

    context = {
        "post": post,
        "is_favourite": is_favourite,
        "dat3": dat3,
        "dat4": dat4,
    }

    return render(request, "article_detail.html", context)

@login_required
def post_favourite_list(request):
    user = request.user
    favourite_posts = user.favourite.all()

    context = {
        "favourite_posts": favourite_posts,
    }
    return render(request, "post_favourite_list.html", context)


def favourite_post(request, slug):
    post = get_object_or_404(Article, slug=slug)
    if post.favourite.filter(id=request.user.id).exists():
        post.favourite.remove(request.user)
    else:
        post.favourite.add(request.user)
    return HttpResponseRedirect(post.get_absolute_url())


@login_required
def post_delete(request, id, slug):
    post = get_object_or_404(Article, slug=slug, id=id)
    user = request.user
    post.favourite.remove(user)
    return redirect("post_favourite_list")


def post_search(request):

    title_q = Q()
    if request.GET.get('title'):
        title_tokens = request.GET.get('title').split()
        for keyword in title_tokens:
            title_q |= Q(title__contains=keyword)

    body_q = Q()
    if request.GET.get('body'):
        body_tokens = request.GET.get('body').split()
        for keyword in body_tokens:
            body_q |= Q(body__contains=keyword)

    price_q = Q()
    if 'price_min' in request.GET:
        if request.GET.get('price_min'):
            price_q &= Q(price__gte=float(request.GET.get('price_min')))

    if 'price_max' in request.GET:
        if request.GET.get('price_max'):
            price_q &= Q(price__lte=float(request.GET.get('price_max')))

    date_min_q = Q()
    if 'date_min' in request.GET:
        if request.GET.get('date_min'):
            d = datetime.datetime.strptime(request.GET.get('date_min'), '%Y-%m-%d')
            tz = timezone.utc
            date_min = tz.localize(d)
            if date_min > datetime.datetime.now(timezone.utc):
                date_min = datetime.datetime.now(timezone.utc)
            date_min_q &= Q(date__gte=date_min)

    date_max_q = Q()
    if 'date_max' in request.GET:
        if request.GET.get('date_max'):
            d = datetime.datetime.strptime(request.GET.get('date_max'), '%Y-%m-%d')
            tz = timezone.utc
            date_max = tz.localize(d)
            if date_max > datetime.datetime.now(timezone.utc):
                date_max = datetime.datetime.now(timezone.utc)
            date_max_q &= Q(date__lte=date_max)

    id_q = Q()
    if request.GET.get('id'):
        id_q &= Q(numb=request.GET.get('id'))

    sort_field = "date"
    if 'sortBy' in request.GET:
        if request.GET.get('sortBy'):
            sort_by = request.GET.get('sortBy')
            sort_field = sort_by.split('-')[0]
            lh_hl = sort_by.split('-')[1]

            if lh_hl == "HL":
                sort_field = "-" + sort_field

    print("lots")
    print(request.GET.get('lots'))

    if request.GET.get('lots'):
        print("lots page")

        q = Q()
        if request.GET.getlist('city[]'):
            city_q = Q()
            for c in request.GET.getlist('city[]'):
                city_q |= Q(city__id=c)
            q &= city_q

        if request.GET.getlist('statzakup[]'):
            stat_q = Q()
            for stat in request.GET.getlist('statzakup[]'):
                stat_q |= Q(statzakup=stat)
            q &= stat_q

        if request.GET.getlist('purchase_method[]'):
            purch_meth = Q()
            for pm in request.GET.getlist('purchase_method[]'):
                purch_meth |= Q(purchase_method=pm)
            q &= purch_meth

        if request.GET.get('id'):
            q &= id_q

        if request.GET.get('title'):
            q &= title_q

        if request.GET.get('body'):
            q &= body_q

        if ('price_min' in request.GET) | ('price_max' in request.GET):
            q &= price_q

        if ('date_min' in request.GET) | ('date_max' in request.GET):
            q &= date_min_q & date_max_q

        print("All filter together")
        print(q)

        print("sort_field")
        print(sort_field)

        if (sort_field == 'title') | (sort_field == '-title'):
            queryset = Article.objects.filter(q)
            if sort_field == '-title':
                sorted_lots = sorted(queryset, key=lambda item: item.title.lower(), reverse=True)
            else:
                sorted_lots = sorted(queryset, key=lambda item: item.title.lower())
        else:
            sorted_lots = Article.objects.filter(q).order_by(sort_field)

        paginator = Paginator(sorted_lots, 25)
        page_number = request.GET.get("page", 1)
        posts = paginator.page(page_number)

        context = {"posts": posts}
        return render(request, "lots-filter-result.html", context)

    q = Q()
    if request.GET.get('city[]'):
        q &= Q(city__id=request.GET.get('city[]')[0])

    if request.GET.get('statzakup'):
        q &= Q(statzakup=request.GET.get('statzakup[]')[0])

    if request.GET.get('purchase_method'):
        q &= Q(purchase_method=request.GET.get('purchase_method[]')[0])

    if request.GET.get('title'):
        q &= title_q

    if request.GET.get('body'):
        q &= body_q

    if request.GET.get('id'):
        q &= id_q

    if ('price_min' in request.GET) | ('price_max' in request.GET):
        q &= price_q

    if ('date_min' in request.GET) | ('date_max' in request.GET):
        q &= date_min_q & date_max_q

    print("All filter together")
    print(q)

    print("sort_field")
    print(sort_field)

    # applying multiple value filters in
    if (sort_field == 'title') | (sort_field == '-title'):
        queryset = Article.objects.filter(q)
        if sort_field == '-title':
            sorted_lots = sorted(queryset, key=lambda item: item.title.lower(), reverse=True)
        else:
            sorted_lots = sorted(queryset, key=lambda item: item.title.lower())
    else:
        sorted_lots = Article.objects.filter(q).order_by(sort_field)

    paginator = Paginator(sorted_lots, 25)
    page_number = request.GET.get("page", 1)
    posts = paginator.page(page_number)

    print("posts.len")
    print(len(posts))

    context = {"posts": posts}

    return render(request, "main_filter_result.html", context)


# def post_search(request):
#     print("views.post_search")
#     isValid = False
#     cities = request.GET.getlist("city[]")
#     purchase_method = request.GET.getlist("purchase_method[]")
#     statzakup = request.GET.getlist("statzakup[]")
#     print(request.GET)
#
#     filters = {
#         k: v
#         for (k, v) in request.GET.items()
#         if k not in ("sortBy", "city[]", "purchase_method[]", "statzakup[]")
#     }
#     for key in filters:
#         if filters[key]:
#             isValid = True
#
#     if not isValid and not (cities or purchase_method or statzakup):
#         # if no filter found only has sort value then onlye sort apply on this
#
#         if request.GET.get("sortBy"):
#             myFilter = Article.objects.order_by(request.GET.get("sortBy"))
#             paginator = Paginator(myFilter, 25)
#             page_number = request.GET.get("page")
#             posts = paginator.get_page(page_number)
#
#             context = {"posts": posts}
#             return render(request, "lots-filter-result.html", context)
#         return render(request, "error.html")
#
#     print("statzakup")
#     print(statzakup)
#     # applying multiple value filters in
#     queryset = Article.objects.filter(
#         Q(city__id__in=cities)
#         | Q(statzakup__in=statzakup)
#         | Q(purchase_method__in=purchase_method)
#     ).order_by(request.GET.get("sortBy", "date"))
#
#     myFilter = ArticleFilter(filters, queryset=queryset)
#     paginator = Paginator(myFilter.qs.order_by("-id"), 25)
#     page_number = request.GET.get("page")
#     posts = paginator.get_page(page_number)
#
#     print("posts")
#     print(len(posts))
#
#     context = {"posts": posts}
#
#     if request.GET.get("lots"):
#         return render(request, "lots-filter-result.html", context)
#     return render(request, "main_filter_result.html", context)


@login_required
def save_favorite_search(request):
    # deleting query from favorites
    if request.POST.get("delete_id"):
        FavoriteSearch.objects.filter(
            id=request.POST.get("delete_id"), user=request.user
        ).delete()
        return JsonResponse({"status": 204, "messsage": "success", "id": None})

    # saving favorites query
    content = request.POST.dict()
    if "city[]" in content:
        content["city[]"] = request.POST.getlist("city[]")

    if "purchase_method[]" in content:
        content["purchase_method[]"] = request.POST.getlist(
            "purchase_method[]")

    if "statzakup[]" in content:
        content["statzakup[]"] = request.POST.getlist("statzakup[]")

    f_search = FavoriteSearch.create(content, request.user)
    f_search.save()
    return JsonResponse({"status": 201, "message": "success", "id": f_search.id})

@login_required
def favorite_search_list(request):
    query = FavoriteSearch.objects.filter(user=request.user).order_by("-id")
    paginator = Paginator(query, 25)
    page_number = request.GET.get("page")
    favorite_searches = paginator.get_page(page_number)
    return render(
        request, "favorite_search_list.html", {
            "favorite_searches": favorite_searches}
    )


@login_required
def remove_favorite_search(request, id):
    # deleting favorite search
    FavoriteSearch.objects.filter(id=id).delete()
    messages.add_message(request, messages.WARNING, "Favorite Search Removed!")
    return redirect(request.GET.get("next"))


def archived_post(request):
    posts = Article.objects.filter(date__lt=timezone.now())
    if request.GET.get('q'):
        q = request.GET.get('q')
        posts = Article.objects.filter(
            (Q(title__icontains=q) |
             Q(body__icontains=q) |
             Q(city__name__icontains=q)) &
            Q(date__lt=timezone.now())
        )
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    posts = paginator.get_page(page_number)

    return render(request, "archived.html", {"posts": posts})
