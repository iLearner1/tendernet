from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


# Create your models here.

class Price(models.Model):

    class TarifChoices(models.TextChoices):
        #MN == MONTH
        MN12 = 'MN12', 'Клиент - на 12 месяцев'
        MN6 = 'MN6', 'Клиент - на 6 месяцев'
        MN3 = 'MN3', 'Клиент - на 3 месяца'
        MN1 = 'MN1', 'Клиент - на 1 месяц'
        EXP_MN12 = 'EXP_MN12', 'Эксперт - на 12 месяцев',
        EXP_MN6 = 'EXP_MN6', 'Эксперт - на 6 месяцев',
        EXP_MN3 = 'EXP_MN3', 'Эксперт - на 3 месяца',
        EXP_MN1 = 'EXP_MN1', 'Эксперт - на 1 месяц',

    name = models.CharField(
        max_length=30,
        db_index=True,
        verbose_name='Название',
        choices=TarifChoices.choices,
        default=TarifChoices.MN1)
    price = models.FloatField(verbose_name='Цена', null=True, default=0)

    def __str__(self):
        try:
           return self.TarifChoices(self.name).label
        except Exception:
            return self.name

    class Meta:
        verbose_name_plural = 'Тарифы'
        verbose_name = 'Тариф'
        ordering = ['name']


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dob = models.DateTimeField(auto_now_add=True, null=True)
    company_business_number = models.CharField(max_length=30, verbose_name="ИИН/БИН", null=True)
    company_name = models.CharField(max_length=256, verbose_name="Наименование компании", null=True)
    tarif = models.ForeignKey('Price', on_delete=models.CASCADE, verbose_name='Тариф',default=None, null=True, blank=True)
    rassylka = models.BooleanField(verbose_name='Подписаться на email рассылку', default=True)
    tarif_expire_date = models.DateTimeField(default=timezone.now() + timezone.timedelta(days=365), null=True, blank=True);

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