from django.core.mail import EmailMessage
from celery import shared_task


@shared_task
def task_tariff_change_email(email, months):
    if months == 2:
        message = 'Через 2 месяца ваш тариф будет автоматический переведен на тариф "Бесплатный".'
    elif months == 3:
        message = 'Через 3 месяца ваш тариф будет автоматический переведен на тариф "Бесплатный".'
    elif months == 6:
        message = 'Через 6 месяцев ваш тариф будет автоматический переведен на тариф "Бесплатный".'
    else:
        message = 'Через 12 месяцев ваш тариф будет автоматический переведен на тариф "Бесплатный"'

    email = EmailMessage("tariff change", message, to=[email])
    email.send()