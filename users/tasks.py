from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from celery import shared_task


@shared_task
def task_tariff_change_email(email, months):
    if months == 3:
        message = 'Через 3 месяца ваш тариф будет автоматический переведен на тариф "Бесплатный".'
    elif months == 6:
        message = 'Через 6 месяцев ваш тариф будет автоматический переведен на тариф "Бесплатный".'
    else:
        message = 'Через 12 месяцев ваш тариф будет автоматический переведен на тариф "Бесплатный"'

    email = EmailMessage("tariff change", message, to=[email])
    email.send()

@shared_task
def send_mail_to_manager(username,email):
    subject, from_email, to = 'Tariff page', settings.DEFAULT_FROM_EMAIL, settings.EMAIL_MANAGER
    msg_html = render_to_string("blocks/tariff-mail.html", {'username': username, 'email': email})
    msg = EmailMessage(subject=subject, body=msg_html, from_email=from_email, to=[settings.EMAIL_MANAGER, 'mdmotailab@gmail.com'])
    msg.content_subtype = "html"  # Main content is now text/html
    return msg.send()