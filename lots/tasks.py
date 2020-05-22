import datetime
import celery
from celery import shared_task, task
from celery.schedules import crontab
from celery.task import periodic_task
from django.core.mail import send_mail
from django.utils import timezone
from .models import Article, FavoriteSearch, Cities
from django.template.loader import render_to_string
from tn_first.settings import CONTACT_MAIL_RECEIVER
from django.core.cache import cache
import requests
from django.template.defaultfilters import slugify


@shared_task
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
            start_date = timezone.utc.localize(datetime.datetime.strptime(response_json['start_date'], '%Y-%m-%d %H:%M:%S'))
            end_date = timezone.utc.localize(datetime.datetime.strptime(response_json['end_date'], '%Y-%m-%d %H:%M:%S'))
            Article.objects.filter(numb=lot_number).update(date=end_date, date_open=start_date)
        except Exception as e:
            print('exception in date update')


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

    response = None
    try:
        response = requests.get(url=URL, headers=header, verify=False)
    except Exception as e:
        print(e)

    count = 0
    data = None
    if response:
        data = response.json()
        print("data.len: ", len(data['items']))

        for item in data["items"]:
            count = count + 1
            # insert 5 lots in each API call
            if item['lot_number'] not in numbs and  count < 6:
                count = count + 1
                numbs.append(item["lot_number"])
                print('inserting lot with lot_number: ', item['lot_number'])
                print('title: ', item['name_ru'])
                print('slugify - title: ', slugify(item['name_ru']))

                article = Article(
                    xml_id=item['lot_number'],
                    customer_bin=item["customer_bin"],
                    title=item["name_ru"],
                    customer=item["customer_name_ru"],
                    price=item["amount"],
                    statzakup=item["ref_trade_methods_id"],
                    numb=item["lot_number"],
                    itemZakup='product',
                    date=datetime.datetime.now(),
                    date_open=datetime.datetime.now(),
                    city=Cities.objects.all()[0],
                    addressFull=item['lot_number'],
                    yst="https://goszakup.gov.kz/ru/announce/index/" + str(item["trd_buy_id"])
                )
                article.save()

                try:
                    celery.execute.send_task('lots.tasks.fetch_date_from_goszakup', (item['trd_buy_id'], item['lot_number']))
                except Exception as e:
                    print('exception in sending task ')
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

    send_mail('new lots arrived', '', 'test@mail.com', [
              'tendernetkz@mail.ru', CONTACT_MAIL_RECEIVER, *receiver], html_message=html, fail_silently=False)


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
