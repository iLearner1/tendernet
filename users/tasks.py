from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from celery import shared_task
from users.models import Profile
from django.utils import timezone

month = {
    'MN12': 12,
    'MN6':  6,
    'MN3':  3,
    'MN1':  1,
    'EXP_MN12':  12,
    'EXP_MN6':  6,
    'EXP_MN3':  3,
    'EXP_MN1':  1,
}

@shared_task
def task_tariff_change_email(email, changed_tarif):
    message = f'Через {month[changed_tarif]} месяца ваш тариф будет автоматический переведен на тариф "Бесплатный".'
    email = EmailMessage("tariff change", message, to=[email])
    email.send()

@shared_task
def send_mail_to_manager(username,email):
    subject, from_email, to = 'Tariff page', settings.DEFAULT_FROM_EMAIL, settings.EMAIL_MANAGER
    msg_html = render_to_string("blocks/tariff-mail.html", {'username': username, 'email': email})
    msg = EmailMessage(subject=subject, body=msg_html, from_email=from_email, to=[settings.EMAIL_MANAGER])
    msg.content_subtype = "html"  # Main content is now text/html
    return msg.send()


@shared_task
def task_before_3days_of_expire_tarif():
    try:
        profiles = Profile.objects.filter(tarif_expire_date__lte=(timezone.now()+timezone.timedelta(days=3)))
        from_email, to =  settings.DEFAULT_FROM_EMAIL, settings.EMAIL_MANAGER

        for profile in profiles:
            msg1 = "Через 3 дня Ваш тарифный план будет сменен на тарифный план Клиент"
            msg2 = f"User {profile.user.username} tarif about to expire in 3 days";

            em1 = EmailMessage("Expire Tarif", msg1, from_email=[from_email], to=[profile.user.email])
            em2 = EmailMessage("Expire Tarif", msg2, from_email=[from_email], to=[to])
            em1.send()
            em2.send()
    except Exception:
        pass


@shared_task
def task_after_expire_tarif():
    try:
        profiles = Profile.objects.filter(
            tarif_expire_date__year=timezone.now().year,
            tarif_expire_date__month=timezone.now().month,
            tarif_expire_date__day=timezone.now().day,
        )
        from_email, to =  settings.DEFAULT_FROM_EMAIL, settings.EMAIL_MANAGER

        for profile in profiles:
            if 'EXP_' in profile.tarif.name:
                profile.tarif.name = "MN12"
                profile.tarif.save()

            msg1 = f'Ваш тарифный план сменен на тарифный план "{"Эксперт" if "EXP_" in profile.tarif.name else "Клиент"}"'
            msg2 = f"User {profile.user.username} tarif has expired today";
            em1 = EmailMessage("Expired Tarif", msg1, from_email=[from_email], to=[profile.user.email])
            em2 = EmailMessage("Expired Tarif", msg2, from_email=[from_email], to=[to])
            em1.send()
    except Exception:
        pass
       

@shared_task
def task_after_3days_of_expire_tarif():
    try:
        profiles = Profile.objects.filter(tarif_expire_date__gte=(timezone.now()+timezone.timedelta(days=3)))
        from_email, to =  settings.DEFAULT_FROM_EMAIL, settings.EMAIL_MANAGER

        for profile in profiles:
            msg1 = "3 Дня назад Ваш тарифный план сменен на тарифный план Клиент"
            msg2 = f"User {profile.user.username} tarif  expired 3 days ago"
            em1 = EmailMessage("Expired Tarif", msg1, from_email=[from_email], to=[profile.user.email])
            em2 = EmailMessage("Expired Tarif", msg2, from_email=[from_email], to=[to])
            em1.send()
            em2.send()

    except Exception:
        pass