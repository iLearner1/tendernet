# Generated by Django 3.0.4 on 2020-05-30 13:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lots', '0017_remove_article_sign_reason_doc_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='favourite',
        ),
    ]