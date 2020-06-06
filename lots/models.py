# articles/models.py
import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
#from django.template.defaultfilters import slugify  # new
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth.models import User
from lots.utils.Choices import PURCHASE_METHOD_CHOICES, SUBJECT_OF_PURCHASE_CHOICES
import cyrtranslit

class Article(models.Model):
    xml_id = models.CharField('Внешний код для Api', null=True, max_length=255)
    customer_bin = models.CharField('Бин организатора', null=True, max_length=255, )
    title = models.CharField(max_length=255, verbose_name='Наименование лота', null=True)
    lotFullName = models.CharField(max_length=255, verbose_name='Полное имя лота', null=True)
    itemZakup = models.CharField(max_length=255, choices=SUBJECT_OF_PURCHASE_CHOICES, default='product', verbose_name='Предмет закупки')
    customer = models.CharField(max_length=255, verbose_name='Заказчик', null=True)
    region = models.ForeignKey('Regions', null=True, on_delete=models.PROTECT, verbose_name='Область')
    city = models.ForeignKey('Cities', null=True, on_delete=models.PROTECT, verbose_name='Город')
    addressFull = models.CharField(max_length=255, verbose_name='Место постаки, полный адресс', null=True)
    numb = models.CharField(max_length=150, verbose_name='Номер лота', null=True)
    price = models.FloatField(verbose_name='Цена', null=True)
    count = models.IntegerField(verbose_name='Количество', null=True)
    unit = models.ForeignKey('Unit', null=True, on_delete=models.PROTECT, verbose_name='Единица измерения')
    statzakup = models.CharField(max_length=10, choices=PURCHASE_METHOD_CHOICES, default='draft', verbose_name='Способ закупки')

    date_open = models.DateTimeField(verbose_name='Дата открытия', null=True)
    date = models.DateTimeField(verbose_name='Дата закрытия', null=True)
    yst = models.URLField(max_length=255, verbose_name='Ссылка', null=True)
    status = models.BooleanField(default=True, verbose_name='Опубликован', db_index=True, null=True)
    slug = models.SlugField(max_length=255, null=False, unique=False)
    favourite = models.ManyToManyField(User, related_name='favourite', blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"id": self.id, "slug": self.slug})

    def save(self, *args, **kwargs):  # new
        print("title: ", self.title)
        print("slug: ", self.slug)
        if not self.slug:
            self.slug = slugify(cyrtranslit.to_latin(self.title).encode('UTF-8', 'ignore'), allow_unicode=True)
        print("slug after: ", self.slug)
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Лоты"
        verbose_name = "Лот"


class Unit(models.Model):
    name = models.CharField(max_length=99, verbose_name='Единица измерения', null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]

class Regions(models.Model):
    code = models.CharField(max_length=30, verbose_name="Код", default=None)
    name = models.CharField(max_length=30, db_index=True, verbose_name="Название")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "районы"
        verbose_name = "Область"
        ordering = ["name"]


class Cities(models.Model):
    code = models.CharField(max_length=30, verbose_name="Код", default=None)
    name = models.CharField(max_length=30, db_index=True, verbose_name="Название")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Города"
        verbose_name = "Город"
        ordering = ["name"]


class FavoriteSearch(models.Model):
    # this model will hold user lots/Article Search prefarance
    search_query = models.TextField(null=True, blank=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="search_query"
    )

    def __str__(self):
        return self.user.username+' Favorite Query'

    @property
    def query(self):
        # converting from text to python dict
        if not self.search_query:
            return None
        return json.loads(self.search_query)

    @classmethod
    def create(cls, search_query, user=None):
        # converting python object to json string for saving to database
        search_query = json.dumps(cls.withOutKey(search_query))
        favorite_search = cls(search_query=search_query, user=user)
        return favorite_search

    def withOutKey(data=None, keys={"csrfmiddlewaretoken", }):
        # keys should be a set
        return {x: data[x] for x in data if x not in keys}

    @property
    def city(self):
        # this method creating a property as like his name and return city object
        query = self.query.get("city[]")
        if type(query) == list:
            return Cities.objects.filter(id__in=query)

    @property
    def statzakup_obj(self):
        query = self.query.get("statzakup[]")
        print("query: ", query)
        q = []
        if type(query) == list:
            for i in query:
                for j in PURCHASE_METHOD_CHOICES:
                    if i in j:
                        q.append(j)
            return q

    @property
    def statzakup(self):
        query = self.query.get("statzakup[]")
        if query != '':
            return query

    @property
    def subject_of_purchase_obj(self):
        query = self.query.get("subject_of_purchase[]")
        q = []
        if type(query) == list:
            for i in query:
                for j in SUBJECT_OF_PURCHASE_CHOICES:
                    if i in j:
                        q.append(j)
            return q

    @property
    def subject_of_purchase(self):
        query = self.query.get("subject_of_purchase[]")
        if type(query) == list:
            return query


# i cant import this on top because of some issues


@receiver(post_save, sender=Article)
def article_save_signal(sender, instance, created, **kwargs):
    from .tasks import notify_subscriber_about_new_lots
    if created:
        notify_subscriber_about_new_lots.delay(instance.id)
