from celery import shared_task
from django.core.mail import send_mail
from tn_first.settings import CONTACT_MAIL_RECEIVER


@shared_task
def task_tariff_change_email(email, months):
    print("users.tasks.task_tariff_change_email.email: ", email)
    html = "<div><<p>Your tariif will be changed to default after " + months + " months</p>/div>"
    send_mail('tariff will be change', '', 'tendernet@mail.com',
              [CONTACT_MAIL_RECEIVER, 'tendernetkz@mail.ru', 'jahangir.08.cse@gmail.com'], html_message=html, fail_silently=False)
    return True
