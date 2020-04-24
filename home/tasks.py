from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from django.template.loader import render_to_string
from tn_first.settings import CONTACT_MAIL_RECEIVER


@shared_task
def send_query(name=None, email=None, message=None, user=None):
    html = render_to_string('blocks/contact-mail.html',
                            {'name': name, 'email': email, 'message': message, 'user': user})
    send_mail('query from/tendernet', '', 'tendernet@mail.com',
              [CONTACT_MAIL_RECEIVER, 'tendernetkz@mail.ru'], html_message=html, fail_silently=False)


@shared_task
def send_consultation_query(name=None, phone=None, user=None):
    html = render_to_string('blocks/consultation-mail.html',
                            {'name': name, 'phone': phone, 'user': user})
    send_mail('Получить консультацию/query', '', 'tendernet@mail.com',
              [CONTACT_MAIL_RECEIVER, 'tendernetkz@mail.ru'], html_message=html, fail_silently=False)
