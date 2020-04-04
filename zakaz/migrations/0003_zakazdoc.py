# Generated by Django 3.0.3 on 2020-02-14 12:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lots', '0008_article_down'),
        ('zakaz', '0002_auto_20200214_1650'),
    ]

    operations = [
        migrations.CreateModel(
            name='Zakazdoc',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('daty', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Дата заявки')),
                ('status', models.CharField(choices=[('draft', 'На рассмотрении'), ('win', 'Выигрыш'), ('sended', 'Заявка отправлено')], default='draft', max_length=10)),
                ('klyenty', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='klyenty', to=settings.AUTH_USER_MODEL)),
                ('lots', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='lots', to='lots.Article')),
            ],
        ),
    ]
