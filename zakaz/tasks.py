from celery import shared_task
from django.core.mail import send_mail
from tn_first.settings import CONTACT_MAIL_RECEIVER, CONTACT_MAIL_SENDER
from django.template.loader import render_to_string


@shared_task
def notify_admin_service(formData, subject):

    html = render_to_string('blocks/service-mail.html', {'form': formData})
    send_mail(subject, '', CONTACT_MAIL_SENDER, [
              CONTACT_MAIL_RECEIVER], fail_silently=False, html_message=html)
