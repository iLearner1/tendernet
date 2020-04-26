from django.db import models
from django.contrib.auth.models import User
from lots.models import Article


class Zakaz(models.Model):
    STATUS_CHOICES = [
    ('draft','На рассмотрении'),
    ('win','В обработке'),
    ('send','Подача заявки'),
    ('sended','Обработан')
    ]
    date = models.DateTimeField(auto_now_add=True, null=True, verbose_name='Дата заявки')
    klyent = models.ForeignKey(User, related_name='klyent', on_delete=models.CASCADE,null=True, blank=True)
    lot = models.ForeignKey(Article, related_name='lot', on_delete=models.CASCADE,null=True,blank=True)
    status  =  models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    zavdate = models.DateTimeField(null=True, verbose_name='Дата завершения')

    class Meta:
        ordering = ['-id']
        verbose_name_plural = 'Заявки на участие'
        verbose_name = 'Заявка на участие'






class Zakazdoc(models.Model):
    STATUS_CHOICES = [
    ('draft','На рассмотрении'),
    ('win','Выигрыш'),
    ('sended','Заявка отправлено')
    ]
    daty = models.DateTimeField(auto_now_add=True, null=True, verbose_name='Дата заявки')
    klyenty = models.ForeignKey(User, related_name='klyenty', on_delete=models.CASCADE,null=True, blank=True)
    lots = models.ForeignKey(Article, related_name='lots', on_delete=models.CASCADE,null=True,blank=True)
    status  =  models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')


    class Meta:
        verbose_name_plural = 'Запросы документов'
        verbose_name = 'Запрос документов'
        ordering = ['-id']



