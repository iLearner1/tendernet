from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Price(models.Model):
    name = models.CharField(max_length=30, db_index=True, verbose_name='Название')
    price = models.FloatField(verbose_name='Цена', null=True, default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Тарифы'
        verbose_name = 'Тариф'
        ordering = ['name']


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dob = models.DateTimeField(auto_now_add=True, null=True)
    # please reconsider this logic, if someone start with a fresh database how would he get value from an empty table 
    # it will throw a an error
    # default=Price.objects.filter(name='free')[0].id
    # price, create = Price.objects.get_or_create(name='Бесплатный тариф')
    tarif = models.ForeignKey('Price', on_delete=models.CASCADE, verbose_name='Тариф',default=None, null=True, blank=True)
    rassylka = models.BooleanField(verbose_name='Подписаться на email рассылку', default=True)

    def __str__(self):
        return "Профиль пользователя {}".format(self.user.username)

    class Meta:
        verbose_name_plural = 'Профили пользователей'
        verbose_name = 'Профиль пользователя'



# @receiver(post_save, sender=User)
# def post_save_profile(sender, instance, **kwargs):
#     if kwargs['created']:
#         price, created = Price.objects.get_or_create(name='Бесплатный тариф')
#         user_profile= Profile(user=instance, tarif_id=price.id)
#         user_profile.save()