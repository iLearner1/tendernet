
import datetime
import celery
from celery import shared_task, task
from celery.schedules import crontab
from celery.task import periodic_task
from django.core.mail import send_mail
from django.utils import timezone
from .models import Article, FavoriteSearch, Cities, Regions
from django.template.loader import render_to_string
from tn_first.settings import CONTACT_MAIL_RECEIVER
from django.core.cache import cache
import requests
from django.template.defaultfilters import slugify
from lots.insert_region_location import read_xls
from time import sleep
from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_aware, make_aware
from lots.utils.fetchLotsFromGraphql import fetchLotsFromGraphql
from django.db.models import Q

@shared_task
def update_location(q):
    print("function -> update_location")
    print(q)
    articles = Article.objects.all()
    nums = []
    for a in articles:
        nums.append(a.numb)
    print("articles.len: ", len(articles))

    print("articles.unik.len: ", len(list(set(nums))))
    i = 0
    for a in articles:
        
        if i < 0:
            print("i: ", i)
            i = i + 1
            print("create task for customer_bin: ", a.customer_bin)
            api_url = "https://ows.goszakup.gov.kz/v3/subject/biin/" + a.customer_bin + "/address"
            update_location_in_article.delay(api_url, a.numb)


        
    
@shared_task
def update_location_in_article(api_url, lot_number):
    print("function -> update_location_in_article")
    #api_url = "https://ows.goszakup.gov.kz/v3/subject/biin/" + customer_bin + "/address"

    token = 'bb28b5ade7629ef512a8b7b9931d04ad'
    bearer_token = 'Bearer ' + token
    header = {'Authorization': bearer_token}

    kato_list = read_xls()

    response = None

    try:
        response = requests.get(url=api_url, headers=header, verify=False)
    except Exception as e:
        print('failed address API call')

    if response:
        response_json = response.json()
        try:
            item = response_json["items"][0]
            kato_code = item["kato_code"]
            if kato_code in kato_list:
                print("in kato_list")
            else:
                print("not in kato_list")
            region_code = kato_code[0:2]+"0000000"
            location_code = kato_code[0:4]+"00000"
            print("code: kato, region, location")
            print(kato_code, region_code, location_code)
            if Article.objects.filter(city=None).exists():
                print("city None exists")
                try:
                    a = Article.objects.filter(city=None).first()
                    print("a.title: ", a.title)
                    print("a.city: ", a.city)
                    print("a.region: ", a.region)
                except Exception as e:
                    print("exception in filter by lot_number: ", e)
        except Exception as e:
            print("kato_code exception: ", e)

@shared_task
def fetch_region_location_from_goszak_1():
    print("fetch location from goszak")
    a = None
    try:
        a = Article.objects.filter(city=None).first()
    except Exception as e:
        print("error in get article with city None")
    if a:
        print("a.customer_bin: ", a.customer_bin )
        print("a.xml_id: ", a.xml_id)
        print("a.numb: ", a.numb)
    if a:
        api_url = "https://ows.goszakup.gov.kz/v3/subject/biin/" + a.customer_bin + "/address"
    token = 'bb28b5ade7629ef512a8b7b9931d04ad'
    bearer_token = 'Bearer ' + token
    header = {'Authorization': bearer_token}
    response = None
    if a:
        try:
            response = requests.get(url=api_url, headers=header, verify=False)
        except Exception as e:
            print("exception in get request")
            print(e)
    if response:
        response_json = response.json()
        try:
            item = response_json["item"][0]
            kato_code = item["kato_code"]
            region_code = kato_code[0:2] + "0000000"
            location_code = kato_code[0:4] + "00000"
            print("region, location: ")
            print(region_code, location_code)
        except Exception as e:
            print("no item in get response")
    else:
        print("else of if response block")
    
@shared_task
def update_existing_lots_region_location():
    print(" Func -> update_existing_lots_region_location")
    a = None
    try:
        a = Article.objects.filter(city=None).filter(region=None).first()
    except Exception as e:
        print("no lot found with city, region None")
    if a:
        print("a.customer_bin: ", a.customer_bin)
        print("a.xml_id: ", a.xml_id)
        fetch_region_location_from_goszak.delay(a.customer_bin, a.xml_id)


@shared_task
def fetch_region_location_from_goszak(customer_bin, lot_number, kato_list={}):
    print("Function -> fetch region/location")
    print("customer_bin: ", customer_bin)
    print("lot_number: ", lot_number)
    api_url = "https://ows.goszakup.gov.kz/v3/subject/biin/" + customer_bin + "/address"

    token = 'bb28b5ade7629ef512a8b7b9931d04ad'
    bearer_token = 'Bearer ' + token
    header = {'Authorization': bearer_token}

    response = None

    try:
        response = requests.get(url=api_url, headers=header, verify=False)
    except Exception as e:
        print(e);
        print('failed address API call')

    if response:
        response_json = response.json()

        try:
            item = response_json["items"][0]
            kato_code = item["kato_code"]

            region_code = kato_code[0:2] + "0000000"
            location_code = kato_code[0:4] + "00000"
            print("region_code: ", region_code)
            print("location_code: ", location_code)
            location_found = False
            location  = None
            try:
                location = Cities.objects.get(code=location_code)
            except Exception as e:
                print("exception in finding cities with location_code: ", location_code)
                print(e)
            print("check if location None: ", location)
            if location:
                location_found = True
                print("if location true/location found in db")
                print("updating lot with location found in db")
                try:
                    a=Article.objects.get(xml_id=lot_number)
                    a.city=location
                    a.save()
                except Exception as e:
                    print("exception updating location found in db with lot number: ", lot_number)
                    print(e)
            region_found = False
            region = None

            try:
                region = Regions.objects.get(code=region_code)
            except Exception as e:
                print("exception in fetching region with region_code: ", region_code)
                print(e)
            print("check if region is None: ", region)

            code_map = {'710000000': ' г. Нур-Султан', '750000000': 'г. Алматы', '790000000': 'г. Шымкент'}
            if region:
                region_found = True
                print("if region true/region found in db")
                print("updating lot with region found in db")
                try:
                    a=Article.objects.get(xml_id=lot_number)
                    a.region=region
                    a.save()
                except Exception as e:
                    print("exception in updating lot with region found in db with lot number: ", lot_number)
                    print(e)


            if location_found:
                print("location found")
            else:
                print("location not found")
                code_map = {'710000000': ' г. Нур-Султан', '750000000': 'г. Алматы', '790000000': 'г. Шымкент'}
                cc = None
                if kato_code in ["710000000", "750000000", "790000000"]:
                    print("kato_code in (71, 75,m 79)")
                    try:
                        cc = Cities()
                        cc.code = kato_code
                        cc.name = code_map[kato_code]
                        cc.save()
                        print("city created successfully with kato_code: ", kato_code)
                        print("city name: ", code_map[kato_code])
                    except Exception as e:
                        print("exception creating city (code in 71, 75, 79) with kato_code: ", kato_code)
                        print(e)
                else:
                    print("kato_code not in (71, 75, 79)")
                    try:
                        cc = Cities()
                        cc.code = location_code
                        cc.name = location_code
                        cc.save()
                        print("city created successfully with location_code: ", location_code)
                    except Exception as e:
                        print("exception creating city, when kato not in (71-79) with location_code: ", location_code)
                        print(e)
                print("check if cc is None: " , cc)
                if cc:
                    print("city created update lot")
                    try:
                        a = Article.objects.get(xml_id=lot_number)
                        a.city = cc
                        a.save()
                        print("lot updated successfully with lot number: ", lot_number)
                        print("city: ", cc)
                    except Exception as e:
                        print("exception updating lot after create city with lot number: ", lot_number)
                        print("with city: ", cc)
                        print(e)
            if region_found:
                print("region found")
            else:
                print("region not found")
                code_map = {'710000000': ' г. Нур-Султан', '750000000': 'г. Алматы', '790000000': 'г. Шымкент'}
                rr = None
                if kato_code in ["710000000", "750000000", "790000000"]:
                    print("kato_code in (71, 75, 79)")
                    try:
                        rr = Regions()
                        rr.code = kato_code
                        rr.name = code_map[kato_code]
                        rr.save()
                        print("region created successfully with kato_code: ", kato_code)
                        print("region name: ", code_map[kato_code])
                    except Exception as e:
                        print("exception creating region when code in (71-79): ", kato_code)
                        print(e)
                else:
                    print("region -> kato_code not in (71, 75, 79)")
                    try:
                        rr = Regions()
                        rr.code = region_code
                        rr.name = region_code
                        rr.save()
                        print("region created successfully with region_code: ", region_code)
                    except Exception as e:
                        print("exception creating region with region_code: ", region_code)                
                if rr:
                    try:
                        a = Article.objects.get(xml_id=lot_number)
                        a.region = rr
                        a.save()
                        print("lot updated successfully with lot_number: ", lot_number)
                        print("region: ", rr)
                    except Exception as e:
                        print("exception updating lot with lot number: ", lot_number)
                        print(e)

            address = item["address"]
            print("address: ", address)
            if address:
                address_split = item["address"].split(",")
                for item in address_split:
                    print("address.part: ", item)
                if '0' in address_split[0]:
                    address_split = address_split[1:]
                    print("address without city: ", address_split)
                    if location:
                        address = location.name + ", " + ", ".join(address_split)
                print("final address: ", address)
                try:
                    a=Article.objects.get(xml_id=lot_number)
                    a.addressFull=address
                    a.save()
                except Exception as e:
                    print("exception in updating address with lot number: ", lot_number)
                    print(e)

            return True
        except Exception as e:
            print("exeption in updating region/location")
            print(e)
            return False


# @shared_task
def fetch_date_from_goszakup(trd_buy_id, lot_number):
    print("Function -> fetch date")
    print("trd_buy_id: ", trd_buy_id)
    print("lot_number: ", lot_number)

    token = 'bb28b5ade7629ef512a8b7b9931d04ad'
    bearer_token = 'Bearer ' + token
    header = {'Authorization': bearer_token}

    trd_buy_id_response = None
    trd_buy_id_url = "https://ows.goszakup.gov.kz/v3/trd-buy/" + str(trd_buy_id)

    try:
        trd_buy_id_response = requests.get(url=trd_buy_id_url, headers=header, verify=False)
    except Exception as e:
        print('failed trd_buy_id API call')

    if trd_buy_id_response:
        print('trd_buy_id_response found')
        response_json = trd_buy_id_response.json()

        try:
            print('start_date: ', response_json['start_date'])
            print('end_date: ', response_json['end_date'])
            print(response_json)
            start_date = timezone.utc.localize(
                datetime.datetime.strptime(response_json['start_date'], '%Y-%m-%d %H:%M:%S'))
            end_date = timezone.utc.localize(datetime.datetime.strptime(response_json['end_date'], '%Y-%m-%d %H:%M:%S'))
            Article.objects.filter(numb=lot_number).update(date=end_date, date_open=start_date)
        except Exception as e:
            print('exception in date update')
    else:
        print("trd_buy_id_response not found")


def get_aware_datetime(date_str):
    ret = parse_datetime(date_str)
    if not is_aware(ret):
        ret = make_aware(ret)
    return ret


@shared_task
def removeExpiredLots():
    print('deleting expired article...')
    try:
        expired = Article.objects.filter(Q(date__lt=timezone.now()) | Q(date=None))
        for item in expired:
            item.delete()
    except Exception as e:
        print(f"some exception occured when deleting expired lots {e}")

@shared_task
def fetch_lots_from_goszakup():
    """
        deleting expired lots if available
    """
    print('deleting expired article...')
    try:
        expired = Article.objects.filter(Q(date__lt=timezone.now()) | Q(date=None))
        for item in expired:
            item.delete()
    except Exception as e:
        print(f"some exception occured when deleting expired lots {e}")
    
    #fetching  200 lots per call and we need 20 for 4000 lots
    for _ in range(20):
        print(f'===== calling graphql {_} ====')
        fetchLotsFromGraphql()





@shared_task
def notify_subscriber_about_new_lots(lotId=None):
    try:
        article = Article.objects.get(id=lotId)  # new lots
        # searching all users favorites list and try to match with there likes
        receiver = findAllFavoriteSearchReceiver(article)
        # here is the logic
        host_url = cache.get('current_url')

        html = render_to_string('blocks/new-lots-mail.html',
                            {'article': article, 'host_url': host_url})
    except Article.DoesNotExist as e:
        pass


#    send_mail('new lots arrived', '', 'test@mail.com', [
#              'tendernetkz@mail.ru', CONTACT_MAIL_RECEIVER, *receiver], html_message=html, fail_silently=False)


def findAllFavoriteSearchReceiver(article):
    favorites = FavoriteSearch.objects.all()
    users = set()

    for favorite in favorites:
        # sorry, :'( for this line of code what is the logic behinde of this line
        # checking this new article has in anyone favorites list or not
        if ((favorite.city and article.city.id in [item.id for item in favorite.city])
                or (favorite.purchase_method and article.purchase_method in [item for item in favorite.purchase_method])
                or (favorite.statzakup and article.statzakup in [item for item in favorite.statzakup])
                or (handleDate(favorite.query, article))
                or (handleDate(favorite.query, article))
                or article.name == favorite.query['title']):
            users.add(favorite.user.email)
    return users


def handleDate(obj1, obj2):
    if not (obj1['date_max'] and obj1['date_min']):
        return False
    return (datetime.datetime.strptime(obj1['date_max'],
                                       '%Y-%m-%d').date() >= obj2.date_open.date() and datetime.datetime.strptime(
        obj1['date_min'], '%Y-%m-%d').date() <= obj2.date.date())


def handlePrice(obj1, obj2):
    if not (obj1['price_max'] or obj1['price_min']):
        return False
    return (float(favorite.query['price_max']) <= article.price and float(favorite.query['price_min']) >= article.price)
