# Generated by Django 3.0.4 on 2020-05-31 20:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lots', '0018_remove_article_favourite'),
    ]

    operations = [
        migrations.CreateModel(
            name='LotFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, null=True, upload_to='media/')),
                ('case', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lots.Article')),
            ],
        ),
    ]
