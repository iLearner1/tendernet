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
from lots.utils.Choices import PURCHASE_METHOD_CHOICES, SUBJECT_OF_PURCHASE_CHOICES
from lots.utils.config import PAGE_SIZE
import logging 
logging.basicConfig(level='DEBUG')
import requests
from users.models import Profile, Price



def post_list(request):

    if request.method == "GET":
        # comes from /lots page OR "Apply to search"
        request_object = request.GET
    else:
        # when it comes from main page with only title
        request_object = request.POST

    q = Q()
    title_q = Q()

    current_time_q = Q(date__gte=timezone.now())
    q &= current_time_q
    print('post list')

    myFilter = {}

    print("request_object")
    print(request_object)

    if 'title' in request_object:
        if request_object.get('title'):
            title_tokens = request_object.get('title').split()
            for keyword in title_tokens:
                title_q |= Q(title__contains=keyword.capitalize())
                title_q |= Q(title__contains=keyword.lower())
                title_q |= Q(title__contains=keyword.upper())

                if request_object.get('searchby3char-home'):
                    title_q |= Q(title__iregex=r"(^|\s)%s" % keyword[:3])
                    title_q |= Q(title__iregex=r"(^|\s)%s" % keyword[:3].lower())
                    title_q |= Q(title__iregex=r"(^|\s)%s" % keyword[:3].upper())
                    title_q |= Q(title__iregex=r"(^|\s)%s" % keyword[:3].capitalize())

        q &= title_q

    customer_q = Q()
    if 'customer' in request_object:
        if request_object.get('customer'):
            customer_tokens = request_object.get('customer').split()
            for keyword in customer_tokens:
                customer_q |= Q(customer_bin__contains=keyword)
        q &= customer_q

    city_q = Q()
    if request_object.getlist('city[]'):
        for c in request_object.getlist('city[]'):
            city_q |= Q(city__id=c)
        q &= city_q

    purchase_method_q = Q()
    if request_object.getlist('statzakup[]'):
        for stat in request_object.getlist('statzakup[]'):
            purchase_method_q |= Q(statzakup=stat)
        q &= purchase_method_q

    purchase_subject_q = Q()
    if request_object.getlist('subject_of_purchase[]'):
        for pm in request_object.getlist('subject_of_purchase[]'):
            purchase_subject_q |= Q(itemZakup=pm)
        q &= purchase_subject_q

    price_q = Q()
    if 'price_min' in request_object:
        if request_object.get('price_min'):
            price_q &= Q(price__gte=float(request_object.get('price_min')))

    if 'price_max' in request_object:
        if request_object.get('price_max'):
            price_q &= Q(price__lte=float(request_object.get('price_max')))

    q &= price_q

    date_min_q = Q()
    if 'date_min' in request_object:
        if request_object.get('date_min'):
            d = datetime.datetime.strptime(request_object.get('date_min'), '%Y-%m-%d')
            tz = timezone.utc
            date_min = tz.localize(d)
            if date_min > datetime.datetime.now(timezone.utc):
                date_min = datetime.datetime.now(timezone.utc)
            date_min_q &= Q(date__gte=date_min)
        q &= date_min_q

    date_max_q = Q()
    if 'date_max' in request_object:
        if request_object.get('date_max'):
            d = datetime.datetime.strptime(request_object.get('date_max'), '%Y-%m-%d')
            tz = timezone.utc
            date_max = tz.localize(d)
            if date_max > datetime.datetime.now(timezone.utc):
                date_max = datetime.datetime.now(timezone.utc)
            date_max_q &= Q(date__lte=date_max)
        q &= date_max_q

    id_q = Q()
    if 'id' in request_object:
        if request_object.get('id'):
            id_q &= Q(id=request_object.get('id'))
            q &= id_q

    filters = {}

    posts = Article.objects.filter(q)
    myFilter = ArticleFilter(filters, queryset=posts)

    paginator = Paginator(posts.order_by("date"), 25)
    page_number = request_object.get("page", 1)
    posts = paginator.page(page_number)

    cities = Cities.objects.all()

    total_posts = paginator.count
    posts_start_index = 0
    posts_end_index = 0

    if len(posts) > 0:
        posts_start_index = (int(page_number) - 1) * 25 + 1
        posts_end_index = (int(page_number) - 1) * 25 + len(posts)

    context = {
        "posts": posts,
        "posts_start_index": posts_start_index,
        "posts_end_index": posts_end_index,
        "total_posts": total_posts,
        "myFilter": myFilter,
        "cities": cities,
        "PURCHASE_METHOD_CHOICES": PURCHASE_METHOD_CHOICES,
        "SUBJECT_OF_PURCHASE_CHOICES": SUBJECT_OF_PURCHASE_CHOICES
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

    tariff = "free"
    try:
        tarif_id = Profile.objects.filter(user__id=request.user.id).values('tarif_id')[0]
        tariff = Price.objects.get(id=tarif_id['tarif_id'])
    except Exception as e:
        print("profile/tarif not found")

    istariff = False
    if tariff == "free":
        istariff = True


    context = {
        "post": post,
        "is_favourite": is_favourite,
        "dat3": dat3,
        "dat4": dat4,
        "istariff": istariff
    }

    return render(request, "article_detail.html", context)

@login_required
def post_favourite_list(request):
    user = request.user
    favourite_posts = user.favourite.all()

    context = {
        "favourite_posts": favourite_posts,
        "current_date": datetime.datetime.now(timezone.utc)
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

    #current_time_q = Q(date__gte=timezone.now())
    current_time_q = Q()

    title_q = Q()
    if request.GET.get('title'):
        title_tokens = request.GET.get('title').split()
        for keyword in title_tokens:
            title_q |= Q(title__contains=keyword.capitalize())
            title_q |= Q(title__contains=keyword.lower())
            title_q |= Q(title__contains=keyword.upper())

            print("3char: ", request.GET.get('searchby3char'))
            if request.GET.get('searchby3char') == "1":
                title_q |= Q(title__iregex=r"(^|\s)%s" % keyword[:3])
                title_q |= Q(title__iregex=r"(^|\s)%s" % keyword[:3].lower())
                title_q |= Q(title__iregex=r"(^|\s)%s" % keyword[:3].upper())
                title_q |= Q(title__iregex=r"(^|\s)%s" % keyword[:3].capitalize())

    print("title_q")
    print(title_q)

    customer_q = Q()
    if request.GET.get('customer'):
        body_tokens = request.GET.get('customer').split()
        for keyword in body_tokens:
            customer_q |= Q(customer_bin__contains=keyword)

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
            date_max_q &= Q(date__lte=date_max)

    id_q = Q()
    if request.GET.get('id'):
        if request.GET.get('id') != '':
            id_q &= Q(numb=request.GET.get('id'))

    sort_field = "date"
    if 'sortBy' in request.GET:
        if request.GET.get('sortBy'):
            sort_by = request.GET.get('sortBy')
            sort_field = sort_by.split('-')[0]
            lh_hl = sort_by.split('-')[1]

            if lh_hl == "HL":
                sort_field = "-" + sort_field

    q = Q()
    if request.GET.getlist('city[]'):
        city_q = Q()
        for c in request.GET.getlist('city[]'):
            if c != '':
                city_q |= Q(city__id=c)
        q &= city_q

    if request.GET.getlist('statzakup[]'):
        stat_q = Q()
        for stat in request.GET.getlist('statzakup[]'):
            if stat != '':
                stat_q |= Q(statzakup=stat)
        q &= stat_q

    if request.GET.getlist('subject_of_purchase[]'):
        purch_subject = Q()
        for pm in request.GET.getlist('subject_of_purchase[]'):
            if pm != '':
                purch_subject |= Q(itemZakup=pm)
        q &= purch_subject


    if request.GET.get('id'):
        q &= id_q

    if request.GET.get('title'):
        q &= title_q

    if request.GET.get('customer'):
        q &= customer_q

    if ('price_min' in request.GET) | ('price_max' in request.GET):
        q &= price_q

    if ('date_min' in request.GET) | ('date_max' in request.GET):
        q &= date_min_q & date_max_q

    q &= current_time_q

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

    total_posts = paginator.count
    posts_start_index = 0
    posts_end_index = 0

    if len(posts) > 0:
        posts_start_index = (page_number - 1) * 25 + 1
        posts_end_index = (page_number - 1) * 25 + len(posts)

    context = {"posts": posts,
               "total_posts": total_posts,
               "posts_start_index": posts_start_index,
               "posts_end_index": posts_end_index
            }
    return render(request, "lots-filter-result.html", context)


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

    if "subject_of_purchase[]" in content:
        content["subject_of_purchase[]"] = request.POST.getlist(
            "subject_of_purchase[]")

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
    print("# deleting favorite search")
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


def api_interface(request):

    if request.method == 'GET':
        api_url = request.GET['api_url']

        token = 'bb28b5ade7629ef512a8b7b9931d04ad'
        bearer_token = 'Bearer ' + token
        header = {'Authorization': bearer_token}

        response = None

        try:
            response = requests.get(url=api_url, headers=header, verify=False)
        except Exception as e:
            print(e)
            return JsonResponse({'status': 'error'})

        if response:
            return JsonResponse({'status': 'success', 'data': response.json()})

    return JsonResponse({'status': 'error'})


def delete_lots(request):
    try:
        delete = Article.objects.all()
        delete.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error'})