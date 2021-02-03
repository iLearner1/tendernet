# lots/views.py
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .filters import ArticleFilter
from .models import Article, FavoriteSearch, Cities, Regions
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
from lots.insert_region_location import read_xls, insert_regions, insert_locations


def getAllXMLID(request):
    articles = Article.objects.all()
    ids = []
    for a in articles:
        ids.append(a.xml_id)
    return JsonResponse({'ids': ids})

def getArticle(request):
    lot = request.GET['lot']
    e = None
    a = None
    try:
        a = Article.objects.get(xml_id=lot)
    except Exception as e:
        excptn = e
    if a:
        return JsonResponse({'status': 'success', 'a.xml_id': a.xml_id, 'a.numb': a.numb})
    else:
        return JsonResponse({'status': 'error', 'e': excptn})


def getLocationList(request):
    kato_list = read_xls()
    cities = Cities.objects.all()
    cities_list = []
    for c in cities:
        cities_list.append(c.code)
    return JsonResponse({'status': 'success', 'codes': kato_list, 'codes.len': len(kato_list), 'cities_list': cities_list, 'cities_list.len': len(cities_list)})

def getLocationByCustomerBin(request):
    kato_list = read_xls()
    bin = request.GET['bin']
    token = 'bb28b5ade7629ef512a8b7b9931d04ad'
    bearer_token = 'Bearer ' + token
    header = {'Authorization': bearer_token}
    api_url = "https://ows.goszakup.gov.kz/v3/subject/biin/" + bin + "/address"
    try:
        response = requests.get(url=api_url, headers=header, verify=False)
    except Exception as e:
        print("except")
    kato_code = None
    location_code = None
    region_code = None
    inKatoList = False
    if response:
        response = response.json()
        item = response["items"][0]
        kato_code = item["kato_code"]
        region_code = kato_code[0:2]+"0000000"
        location_code = kato_code[0:4]+"00000"
        if kato_code in kato_list:
            inKatoList = True
    return JsonResponse({'status': 'success', 'kato_code': kato_code, 'location_code': location_code, 'region_code': region_code, 'inKatoList': inKatoList})


def getAllCustomerBin(request):
    kato_list = read_xls()
    articles = Article.objects.all()
    bins = []
    cities = []
    bins_without_city = []
    city_in_kato_list = []
    city_not_in_kato_list = []
    for a in articles:
        bins.append(a.customer_bin)
        if a.city:
            cities.append(a.city.code)
        else:
            bins_without_city.append(a.customer_bin)
        if a.city:
            if a.city.code in kato_list.keys():
                city_in_kato_list.append(a.city.code)
            else:
                city_not_in_kato_list.append(a.city.code)
        
    
    return JsonResponse({'status': 'success', 'length': len(bins), 'cities.len': len(cities), 'bins_without_city.len': len(bins_without_city), 'bins_without_city': bins_without_city, 'city_in_kato_list': city_in_kato_list, 'city_not_in_kato_list': city_not_in_kato_list, 'city_in_kato_list.len': len(city_in_kato_list), 'city_not_in_kato_list.len': len(city_not_in_kato_list)})

def getAllUnikCustomerBin(request):
    articles = Article.objects.all()
    bins = []
    all_bins = []
    for a in articles:
        if a.customer_bin not in bins:
            bins.append(a.customer_bin)
        all_bins.append(a.customer_bin)
    using_set = list(set(all_bins))
    return JsonResponse({'status': 'success', 'using_in_len': len(bins), 'using_set_len': len(using_set), 'all_bin_len': len(all_bins), 'using_in': bins, 'using_set': using_set, 'all_bins': all_bins})


def insert_regions_locations(request):
    insert_locations()
    insert_regions()
    return JsonResponse({'status': 'success'})

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

    myFilter = {}

    if 'title' in request_object:
        if request_object.get('title'):
            title_tokens = request_object.get('title').split()
            for keyword in title_tokens:
                title_q |= Q(title__contains=keyword.capitalize())
                title_q |= Q(title__contains=keyword.lower())
                title_q |= Q(title__contains=keyword.upper())

                # if request_object.get('searchby3char-home'):
                if len(keyword) <= 5:
                    title_q |= Q(title__iregex=r"(^|\s)%s" % keyword[:3])
                    title_q |= Q(title__iregex=r"(^|\s)%s" % keyword[:3].lower())
                    title_q |= Q(title__iregex=r"(^|\s)%s" % keyword[:3].upper())
                    title_q |= Q(title__iregex=r"(^|\s)%s" % keyword[:3].capitalize())

                if len(keyword) >= 6:
                    title_q |= Q(title__iregex=r"(^|\s)%s" % keyword[:5])
                    title_q |= Q(title__iregex=r"(^|\s)%s" % keyword[:5].lower())
                    title_q |= Q(title__iregex=r"(^|\s)%s" % keyword[:5].upper())
                    title_q |= Q(title__iregex=r"(^|\s)%s" % keyword[:5].capitalize())

        q &= title_q

    customer_q = Q()
    if 'customer' in request_object:
        if request_object.get('customer'):
            customer_tokens = request_object.get('customer').split()
            customer_q |= Q(customer_bin=customer_tokens[0])
            for keyword in customer_tokens:
                customer_q |= Q(customer__contains=keyword.lower())
                customer_q |= Q(customer__contains=keyword.upper())
                customer_q |= Q(customer__contains=keyword.capitalize())

                if len(keyword) <= 5:
                    customer_q |= Q(customer__iregex=r"(^|\s)%s" % keyword[:3])
                    customer_q |= Q(customer__iregex=r"(^|\s)%s" % keyword[:3].lower())
                    customer_q |= Q(customer__iregex=r"(^|\s)%s" % keyword[:3].upper())
                    customer_q |= Q(customer__iregex=r"(^|\s)%s" % keyword[:3].capitalize())

                if len(keyword) >=6:
                    customer_q |= Q(customer__iregex=r"(^|\s)%s" % keyword[:5])
                    customer_q |= Q(customer__iregex=r"(^|\s)%s" % keyword[:5].lower())
                    customer_q |= Q(customer__iregex=r"(^|\s)%s" % keyword[:5].upper())
                    customer_q |= Q(customer__iregex=r"(^|\s)%s" % keyword[:5].capitalize())
        q &= customer_q

    itemZakup_q = Q()
    if request.GET.get('itemZakup'):
        itemZakup_q |= Q(itemZakup=request.GET.get('itemZakup'))
        q &= itemZakup_q

    city_q = Q()
    city_selected = False
    if request.GET.get('city'):
        city_selected = True
        city_q |= Q(city__code=request.GET.get('city'))
        q &= city_q

    region_q = Q()
    if request.GET.get('region'):
        region_q |= Q(region__code=request.GET.get('region'))
        q &= region_q

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

    date_max_q = Q()
    if 'date_max' in request_object:
        if request_object.get('date_max'):
            d = datetime.datetime.strptime(request_object.get('date_max'), '%Y-%m-%d')
            tz = timezone.utc
            date_max = tz.localize(d)
            date_max_q &= Q(date__lte=date_max)

    id_q = Q()
    if 'id' in request_object:
        if request_object.get('id'):
            id_q &= Q(id=request_object.get('id'))
            q &= id_q

    filters = {}

    queryset = Article.objects.order_by('-date_created','-date').filter(q) 
    # sorted_lots = sorted(queryset, key=lambda item: item.title.lower())
    paginator = Paginator(queryset, 25)
    page_number = request.GET.get("page", 1)
    posts = paginator.page(page_number)
    cities = Cities.objects.all()
    regions = Regions.objects.all()
    regions = [region for region in regions if not region.name.isdigit()]
    total_posts = paginator.count
    posts_start_index = 0
    posts_end_index = 0

    if len(posts) > 0:
        posts_start_index = (int(page_number) - 1) * 25 + 1
        posts_end_index = (int(page_number) - 1) * 25 + len(posts)

    context = {
        "city_selected": city_selected,
        "posts": posts,
        "posts_start_index": posts_start_index,
        "posts_end_index": posts_end_index,
        "total_posts": total_posts,
        "myFilter": myFilter,
        "total_pages":paginator.num_pages,
        "cities": cities,
        "regions":regions,
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
    post_request = None

    is_favourite = False
    try:
        is_favourite = post.favourite.filter(id=request.user.id).exists()
    except Exception as e:
        print("not exists")

    tariff = "Бесплатный тариф"
    istariff = False
    try:
        tarif_id = Profile.objects.filter(user__id=request.user.id).values('tarif_id')[0]
        tariff = Price.objects.get(id=tarif_id['tarif_id'])

        if tariff:
            if tariff.name == "Бесплатный тариф":
                istariff = True

    except Exception as e:
        print("profile/tarif not found")


    try:
        queryset = post.lot.all().order_by('-date')
        paginator = Paginator(queryset, 25)
        page_number = request.GET.get("page", 1)
        post_requests = paginator.page(page_number)
        total_pages = paginator.num_pages
    except Exception as e:
        print("Exception Ocured ", e)

    context = {
        "post": post,
        "is_favourite": is_favourite,
        "dat3": dat3,
        "istariff": istariff,
        "post_requests": post_requests,
        'total_pages': total_pages
    }
    
    if request.is_ajax():
        return render(request, 'blocks/request-partial.html', context)

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


def favourite_post_ajax(request, ID):

    post = get_object_or_404(Article, id=ID)
    if post.favourite.filter(id=request.user.id).exists():
        post.favourite.remove(request.user)
        return JsonResponse({'added': False})
    else:
        post.favourite.add(request.user)
        return JsonResponse({'added': True})



def favourite_post(request, ID):
    post = get_object_or_404(Article, id=ID)
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
    if not request.is_ajax():
        return redirect('post_list')
    
    current_time_q = Q(date__gte=timezone.now())
    title_q = Q()
    if request.GET.get('title'):
        title_tokens = request.GET.get('title').split()

        print("title_tokens.len: ", len(title_tokens))
        print("title_tokens")
        print(title_tokens)

        for keyword in title_tokens:
            title_q |= Q(title__contains=keyword.capitalize())
            title_q |= Q(title__contains=keyword.lower())
            title_q |= Q(title__contains=keyword.upper())

            # print("3char: ", request.GET.get('searchby3char'))
            # if request.GET.get('searchby3char') == "1":
            if len(keyword) <= 5:
                title_q |= Q(title__iregex=r"(^|\s)%s" % keyword[:3])
                title_q |= Q(title__iregex=r"(^|\s)%s" % keyword[:3].lower())
                title_q |= Q(title__iregex=r"(^|\s)%s" % keyword[:3].upper())
                title_q |= Q(title__iregex=r"(^|\s)%s" % keyword[:3].capitalize())

            if len(keyword) >=6:
                title_q |= Q(title__iregex=r"(^|\s)%s" % keyword[:5])
                title_q |= Q(title__iregex=r"(^|\s)%s" % keyword[:5].lower())
                title_q |= Q(title__iregex=r"(^|\s)%s" % keyword[:5].upper())
                title_q |= Q(title__iregex=r"(^|\s)%s" % keyword[:5].capitalize())
                



    customer_q = Q()
    if request.GET.get('customer'):
        body_tokens = request.GET.get('customer').split()
        customer_q |= Q(customer_bin=body_tokens[0])
        for keyword in body_tokens:
            customer_q |= Q(customer__contains=keyword.lower())
            customer_q |= Q(customer__contains=keyword.upper())
            customer_q |= Q(customer__contains=keyword.capitalize())
        
            if len(keyword) <= 5:
                customer_q |= Q(customer__iregex=r"(^|\s)%s" % keyword[:3])
                customer_q |= Q(customer__iregex=r"(^|\s)%s" % keyword[:3].lower())
                customer_q |= Q(customer__iregex=r"(^|\s)%s" % keyword[:3].upper())
                customer_q |= Q(customer__iregex=r"(^|\s)%s" % keyword[:3].capitalize())

            if len(keyword) >=6:
                customer_q |= Q(customer__iregex=r"(^|\s)%s" % keyword[:5])
                customer_q |= Q(customer__iregex=r"(^|\s)%s" % keyword[:5].lower())
                customer_q |= Q(customer__iregex=r"(^|\s)%s" % keyword[:5].upper())
                customer_q |= Q(customer__iregex=r"(^|\s)%s" % keyword[:5].capitalize())

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
            id_q &= Q(id=request.GET.get('id'))

    sort_field = "date"
    # if 'sortBy' in request.GET:
    #     if request.GET.get('sortBy'):
    #         sort_by = request.GET.get('sortBy')
    #         sort_field = sort_by.split('-')[0]
    #         lh_hl = sort_by.split('-')[1]
    #
    #         if lh_hl == "HL":
    #             sort_field = "-" + sort_field

    q = Q()

    itemZakup_q = Q()
    if request.GET.get('itemZakup'):
        itemZakup_q |= Q(itemZakup=request.GET.get('itemZakup'))
        q &= itemZakup_q

    city_q = Q()
    if request.GET.get('city'):
        city_q |= Q(city__code=request.GET.get('city'))
        q &= city_q

    region_q = Q()
    if request.GET.get('region'):
        region_q |= Q(region__code=request.GET.get('region'))
        q &= region_q

    # if request.GET.getlist('statzakup[]'):
    #     stat_q = Q()
    #     for stat in request.GET.getlist('statzakup[]'):
    #         if stat != '':
    #             stat_q |= Q(statzakup=stat)
    #     q &= stat_q
    #
    # if request.GET.getlist('subject_of_purchase[]'):
    #     purch_subject = Q()
    #     for pm in request.GET.getlist('subject_of_purchase[]'):
    #         if pm != '':
    #             purch_subject |= Q(itemZakup=pm)
    #     q &= purch_subject

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
    # if (sort_field == 'title') | (sort_field == '-title'):
    #     queryset = Article.objects.filter(q)
    #     if sort_field == '-title':
    #         sorted_lots = sorted(queryset, key=lambda item: item.title.lower(), reverse=True)
    #     else:
    #         sorted_lots = sorted(queryset, key=lambda item: item.title.lower())
    # else:
    #     sorted_lots = Article.objects.filter(q).order_by(sort_field)
    queryset = Article.objects.order_by('-date_created').filter(q)
    # sorted_lots = sorted(queryset, key=lambda item: item.title.lower())
    paginator = Paginator(queryset, 25)
    page_number = request.GET.get("page", 1)
    posts = paginator.page(page_number)
    total_posts = paginator.count
    posts_start_index = 0
    posts_end_index = 0

    if len(posts) > 0:
        posts_start_index = (int(page_number) - 1) * 25 + 1
        posts_end_index = (int(page_number) - 1) * 25 + len(posts)

    context = {"posts": posts,
               "total_posts": total_posts,
               "total_pages": paginator.num_pages,
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

    # if "city[]" in content:
    #     content["city[]"] = request.POST.getlist("city[]")
    #
    # if "subject_of_purchase[]" in content:
    #     content["subject_of_purchase[]"] = request.POST.getlist(
    #         "subject_of_purchase[]")
    #
    # if "statzakup[]" in content:
    #     content["statzakup[]"] = request.POST.getlist("statzakup[]")

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


def region_change_ajax(request):
    region_code = request.POST.get("region_code")
    regions = None
    cities = None
    regions = Regions.objects.filter(code=region_code)

    if regions:
        region= regions[0]
        region_code = region.code
        locations = read_xls()

        filtered_locations = []
        for k, v in locations.items():
            if region_code[0:2] == k[0:2]:
                filtered_locations.append(k)

        if len(filtered_locations) > 0:
            cities = Cities.objects.filter(code__in=filtered_locations)

            return JsonResponse({'status': 'success', 'data': serializers.serialize('json', cities)})

    return JsonResponse({'status': 'failed'})


def delete_lots(request):
    try:
        delete = Article.objects.all()
        delete.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error'})
