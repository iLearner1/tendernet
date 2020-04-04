from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dob = models.DateTimeField(auto_now_add=True, null=True)
    tarif = models.ForeignKey('Price', on_delete=models.CASCADE, verbose_name='Тариф', default='1', )
    rassylka = models.BooleanField(default=True)

    def __str__(self):
        return "Профиль пользователя {}".format(self.user.username)

    class Meta:
        verbose_name_plural = 'Профили пользователей'
        verbose_name = 'Профиль пользователя'


class Price(models.Model):
    name = models.CharField(max_length=30, db_index=True, verbose_name='Название')
    price = models.FloatField(verbose_name='Цена', null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Тарифы'
        verbose_name = 'Тариф'
        ordering = ['name']

