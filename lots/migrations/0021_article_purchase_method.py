# Generated by Django 3.0.4 on 2020-04-13 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lots', '0020_favoritesearch'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='purchase_method',
            field=models.CharField(choices=[('product', 'Товар'), ('services', 'Услуги'), ('job', 'Работа')], default='product', max_length=10, verbose_name='Предмет закупки'),
        ),
    ]