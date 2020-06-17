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

@shared_task
def fetch_region_location_from_goszak(customer_bin, lot_number, kato_list={}):
    print("customer_bin: ", customer_bin)
    print("lot_number: ", lot_number)
    api_url = "https://ows.goszakup.gov.kz/v3/subject/biin/"+ customer_bin +"/address"

    token = 'bb28b5ade7629ef512a8b7b9931d04ad'
    bearer_token = 'Bearer ' + token
    header = {'Authorization': bearer_token}

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
            print("kato_code: ", kato_code)

            region_code = kato_code[0:2] + "0000000"
            location_code = kato_code[0:4] + "00000"
            print("region_code: ", region_code)
            print("location_code: ", location_code)

            location = Cities.objects.filter(code=location_code)
            print("location: ", location)
            if location:
                location = location[0]
                Article.objects.filter(numb=lot_number).update(city=location)
            else:
                print("else location")
                kato_list_keys = list(kato_list.keys())
                if location_code in kato_list_keys:
                    print("if location_code in kato_list_keys")
                    city = Cities()
                    city.name = kato_list[location_code]
                    city.code = location_code
                    city.save()
                    print("city: ", city)
                    location = city
                    Article.objects.filter(numb=lot_number).update(city=city)

            region = Regions.objects.filter(code=region_code)
            if region:
                print("if region")
                print("region_code: ", region_code)
                Article.objects.filter(numb=lot_number).update(region=region[0])
                print("kato_code.type: ", type(kato_code))
                if kato_code in ["710000000", "750000000", "790000000"]:
                    print("kato_code: ", kato_code)
                    print("region[0]: ", region[0])
                    print("region.code: ", region[0].code)
                    print("region.name: ", region[0].name)
                    city = Cities()
                    city.code = region[0].code
                    city.name = region[0].name
                    city.save()
                    Article.objects.filter(numb=lot_number).update(city=city)

            address = item["address"]
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
                Article.objects.filter(numb=lot_number).update(addressFull=address)

            return True
        except Exception as e:
            print("exeption in updating region/location")
            return False


# @shared_task
def fetch_date_from_goszakup(trd_buy_id, lot_number):
    print("trd_buy_id: ", trd_buy_id)
    print("lot_number: ", lot_number)
    try:
        print('slugify - test: ', slugify('asd'))
    except Exception as e:
        print('slugify exception')

    try:
        print('slugify test 2: ', slugify('asd 123'))
    except Exception as e:
        print('slugify test 2 exception')

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
        print('trd_buy_id_response')
        print(trd_buy_id_response.json())
        response_json = trd_buy_id_response.json()

        try:
            print('start_date: ', response_json['start_date'])
            print('end_date: ', response_json['end_date'])
            print(response_json)
            start_date = timezone.utc.localize(datetime.datetime.strptime(response_json['start_date'], '%Y-%m-%d %H:%M:%S'))
            end_date = timezone.utc.localize(datetime.datetime.strptime(response_json['end_date'], '%Y-%m-%d %H:%M:%S'))
            Article.objects.filter(numb=lot_number).update(date=end_date, date_open=start_date)
        except Exception as e:
            print('exception in date update')



def get_aware_datetime(date_str):
    ret = parse_datetime(date_str)
    if not is_aware(ret):
        ret = make_aware(ret)
    return ret

@shared_task
def fetch_lots_from_goszakup():
    # defining a params dict for the parameters to be sent to the API
    token = 'bb28b5ade7629ef512a8b7b9931d04ad'
    bearer_token = 'Bearer ' + token
    header = {'Authorization': bearer_token}

    # api-endpoint
    print("calling goszakup API")
    URL = "https://ows.goszakup.gov.kz/v3/lots"
    articles = Article.objects.all()
    print("articlees.len: ", len(articles))

    numbs = []
    for a in articles:
        if a.numb not in numbs:
            numbs.append(a.numb)
    print('numbs: ', numbs)

    kato_list = read_xls()

    response = None
    try:
        response = requests.get(url=URL, headers=header, verify=False)
    except Exception as e:
        print(e)

    count = 0
    data = None
    lot_trd_list = []
    lot_bin_pair_list = []
    if response:
        data = response.json()
        print("data.len: ", len(data['items']))

        for item in data["items"]:
            count = count + 1
            # insert 5 lots in each API call
            if item['lot_number'] not in numbs:
                count = count + 1
                numbs.append(item["lot_number"])
                print("count: ", count)
                print('inserting lot with lot_number: ', item['lot_number'])

                article = Article(
                    xml_id=item['lot_number'],
                    customer_bin=item["customer_bin"],
                    title=item["name_ru"],
                    lotFullName=item['description_ru'],
                    customer=item["customer_name_ru"],
                    price=item["amount"],
                    statzakup=item["ref_trade_methods_id"],
                    numb=item["lot_number"],
                    itemZakup='product',
                    date=datetime.datetime.now(),
                    date_open=datetime.datetime.now(),
                    yst="https://goszakup.gov.kz/ru/announce/index/" + str(item["trd_buy_id"])+"?tab=documents"
                )
                article.save()
                # lot_trd_list.append((item['trd_buy_id'], item['lot_number']))
                lot_bin_pair_list.append((item['customer_bin'], item['lot_number']))

                #updating article start and end date from api
                token = 'bb28b5ade7629ef512a8b7b9931d04ad'
                bearer_token = 'Bearer ' + token
                header = {'Authorization': bearer_token}

                trd_buy_id_response = None
                trd_buy_id_url = "https://ows.goszakup.gov.kz/v3/trd-buy/" + str(item['trd_buy_id'])

                try:
                    trd_buy_id_response = requests.get(url=trd_buy_id_url, headers=header, verify=False)
                    if trd_buy_id_response:
                        article.date_open = get_aware_datetime(trd_buy_id_response.json()['start_date'])
                        article.date =  get_aware_datetime(trd_buy_id_response.json()['end_date'])
                        article.save()
                        print('updating datetime of lots');
                except Exception as e:
                    print('failed trd_buy_id API call')

               
                

        # if len(lot_trd_list)>0:
        #     while len(lot_trd_list)>0:
        #         print("creating trd task")
        #         result = fetch_date_from_goszakup.delay(lot_trd_list[0][0],lot_trd_list[0][1])
        #         while not result.ready():
        #             print("sleeping for 0.5s")
        #             sleep(0.5)

        #         print("returned from task")
        #         lot_trd_list = lot_trd_list[1:]
        #         print("lot_trd_list.len: ", len(lot_trd_list))

        if len(lot_bin_pair_list) > 0:
            while len(lot_bin_pair_list) > 0:
                print("creating task")
                result = fetch_region_location_from_goszak.delay(lot_bin_pair_list[0][0],lot_bin_pair_list[0][1], kato_list)
                while not result.ready():
                    print("sleeping for 0.5s")
                    sleep(0.5)
                print("returned from task")
                lot_bin_pair_list = lot_bin_pair_list[1:]
                print("lot_bin_pair_list.len: ", len(lot_bin_pair_list))
    else:
        print("no data found from goszakup API")


@shared_task
def notify_subscriber_about_new_lots(lotId=None):
    article = Article.objects.get(id=lotId)  # new lots
    # searching all users favorites list and try to match with there likes
    receiver = findAllFavoriteSearchReceiver(article)
    # here is the logic
    host_url = cache.get('current_url')

    html = render_to_string('blocks/new-lots-mail.html',
                            {'article': article, 'host_url': host_url})

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
    return (datetime.datetime.strptime(obj1['date_max'], '%Y-%m-%d').date() >= obj2.date_open.date() and datetime.datetime.strptime(obj1['date_min'], '%Y-%m-%d').date() <= obj2.date.date())


def handlePrice(obj1, obj2):
    if not (obj1['price_max'] or obj1['price_min']):
        return False
    return (float(favorite.query['price_max']) <= article.price and float(favorite.query['price_min']) >= article.price)