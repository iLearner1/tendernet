# articles/models.py
from django.db import models
from django.template.defaultfilters import slugify # new
from django.urls import reverse
from django.contrib.auth.models import User

class Article(models.Model):
    ZAKUP_CHOICES = [
    ('draft','Запрос ценовых предложении'),
    ('win','Конкурс'),
    ('sended','Аукцион')
    ]


    title = models.CharField(max_length=255, verbose_name='Наименование лота')
    body = models.CharField(max_length=255, verbose_name='Заказчик:')
    city = models.ForeignKey('Cities', null=True, on_delete=models.PROTECT, verbose_name='Город')
    numb = models.CharField(max_length=150, verbose_name='Номер лота', null=True)
    price = models.FloatField(verbose_name='Цена', null=True)
    statzakup = models.CharField(max_length=10, choices=ZAKUP_CHOICES, default='draft', verbose_name='Способ закупки')
    date = models.DateTimeField(verbose_name='Дата закрытия:', null=True)
    date_open = models.DateTimeField(verbose_name='Дата открытия:', null=True)
    yst = models.URLField(max_length=255, verbose_name='Ссылка', null=True)
    down = models.FileField(upload_to='media/', verbose_name='Документы для закгрузки', null=True)
    status = models.BooleanField(default=True, verbose_name='Опубликован', db_index=True)
    slug = models.SlugField(null=False, unique=True)
    favourite = models.ManyToManyField(User, related_name='favourite', blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'id': self.id, 'slug': self.slug})

    def save(self, *args, **kwargs): # new
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Лоты'
        verbose_name = 'Лот'

class Cities(models.Model):
	name = models.CharField(max_length = 30, db_index = True, verbose_name = 'Название')

	def __str__(self):
		return self.name

	class Meta:
		verbose_name_plural = 'Города'
		verbose_name = 'Город'
		ordering = ['name']

