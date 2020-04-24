# articles/models.py
import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from django.template.defaultfilters import slugify  # new
from django.urls import reverse
from django.contrib.auth.models import User
from lots.utils.Choices import ZAKUP_CHOICES, PURCHASE_CHOICES


class Article(models.Model):
    xml_id = models.BigIntegerField('Внешний код для Api', null=True)
    customer_bin = models.CharField('Бин организатора', null=True, max_length=255, )
    totalLots = models.FloatField(verbose_name='Кол-во лотов в объявлении', null=True)
    title = models.CharField(max_length=255, verbose_name='Наименование лота', null=True)
    itemZakup = models.CharField(max_length=255, verbose_name='Предмет закупки', null=True)
    address = models.CharField(max_length=255, verbose_name='Место поставки', null=True)
    addressFull = models.CharField(max_length=255, verbose_name='Место постаки, полный адресс', null=True)
    body = models.CharField(max_length=255, verbose_name='Заказчик:', null=True)
    city = models.ForeignKey('Cities', null=True, on_delete=models.PROTECT, verbose_name='Город')
    numb = models.CharField(max_length=150, verbose_name='Номер лота', null=True)
    price = models.FloatField(verbose_name='Цена', null=True)
    statzakup = models.CharField(max_length=10, choices=ZAKUP_CHOICES, default='draft', verbose_name='Способ закупки')

    date = models.DateTimeField(verbose_name='Дата закрытия:', null=True, default=True)
    date_open = models.DateTimeField(verbose_name='Дата открытия:', null=True, default=True)
    yst = models.URLField(max_length=255, verbose_name='Ссылка', null=True)
    sign_reason_doc_name = models.CharField('Наименование подтверждающего документа', max_length=255, null=True)
    down = models.FileField(upload_to='media/', verbose_name='Документы для загрузки', null=True)
    status = models.BooleanField(default=True, verbose_name='Опубликован', db_index=True, null=True)
    slug = models.SlugField(null=False, unique=False)
    favourite = models.ManyToManyField(User, related_name='favourite', blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"id": self.id, "slug": self.slug})

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Лоты"
        verbose_name = "Лот"


class Cities(models.Model):
    name = models.CharField(max_length=30, db_index=True,
                            verbose_name="Название")

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
        if query:
            return Cities.objects.filter(id__in=query)

    @property
    def purchase_method(self):
        query = self.query.get("purchase_method[]")
        if query:
            return query

    @property
    def statzakup(self):
        query = self.query.get("statzakup[]")
        if query:
            return query


# i cant import this on top because of some issues


@receiver(post_save, sender=Article)
def article_save_signal(sender, instance, created, **kwargs):
    from .tasks import notify_subscriber_about_new_lots
    if created:
        notify_subscriber_about_new_lots.delay(instance.id)
