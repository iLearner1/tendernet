# Generated by Django 3.0.4 on 2020-08-23 10:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lots', '0008_auto_20200819_2102'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='statzakup',
            field=models.CharField(choices=[('draft', 'Запрос ценовых предложении'), ('win', 'Конкурс'), ('sended', 'Аукцион')], default='draft', max_length=255, verbose_name='Способ закупки'),
        ),
    ]
