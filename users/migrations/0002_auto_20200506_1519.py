# Generated by Django 3.0.4 on 2020-05-06 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='rassylka',
            field=models.BooleanField(default=True, verbose_name='Подписаться на email рассылку'),
        ),
    ]
