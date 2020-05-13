import datetime
from celery import shared_task, task
from celery.schedules import crontab
from celery.task import periodic_task
from django.core.mail import send_mail
from django.utils import timezone
from .models import Article, FavoriteSearch
from django.template.loader import render_to_string
from tn_first.settings import CONTACT_MAIL_RECEIVER
from django.core.cache import cache


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
            if item["lot_number"] not in numbs and count < 6:
                numbs.append(item["lot_number"])
                print('inserting lot with lot_number: ', item['lot_number'])

                article = Article(
                    customer_bin=item["customer_bin"],
                    title=item["name_ru"],
                    customer=item["description_ru"],
                    price=item["amount"],
                    totalLots=item["count"],
                    statzakup=item["ref_trade_methods_id"],
                    numb=item["lot_number"],
                    itemZakup='product',
                    date=datetime.datetime.now(),
                    date_open=datetime.datetime.now(),
                    city=None,
                    addressFull=None,
                    yst="https://goszakup.gov.kz/ru/announce/index/" + str(item["trd_buy_id"])
                )
                article.save()
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