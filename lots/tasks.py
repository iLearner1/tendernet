import datetime
from celery import shared_task, task
from django.core.mail import send_mail
from django.utils import timezone
from .models import Article, FavoriteSearch
from django.template.loader import render_to_string
from tn_first.settings import CONTACT_MAIL_RECEIVER
from django.core.cache import cache


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

