from django.contrib import messages

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from zakaz.models import Zakaz, Zakazdoc
from django.views import View
from . import forms
from .tasks import notify_admin_service
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from tn_first.settings import EMAIL_MANAGER


def basket_adding_lot(request):
    return_dict = dict()
    current_site = get_current_site(request)
    data = request.POST
    product_id = data.get("product_id")

    new_product = Zakaz.objects.get_or_create(
        lot_id=product_id, klyent_id=request.user.id,)

    mail_subject = "Участвовать"

    message = render_to_string('blocks/participate_email.html', {
        'phone': request.user.username,
        'name': request.user.first_name + " " + request.user.last_name,
        'email': request.user.email,
        'url': data.get("request_path"),
        'domain': current_site.domain
    })

    send_mail(mail_subject, '', 'tendernet.kz@mail.com',
              [EMAIL_MANAGER], html_message=message, fail_silently=False)

    return JsonResponse(return_dict)


def basket_adding_doc(request):
    return_dict = dict()
    current_site = get_current_site(request)
    data = request.POST
    product_id = data.get("product_id")
    user_id = data.get("user_id")
    new_product = Zakazdoc.objects.get_or_create(
        lots_id=product_id, klyenty_id=user_id,)

    mail_subject = "Запросить аудит"

    message = render_to_string('blocks/participate_email.html', {
        'phone': request.user.username,
        'name': request.user.first_name + " " + request.user.last_name,
        'email': request.user.email,
        'url': data.get("request_path"),
        'domain': current_site.domain
    })

    send_mail(mail_subject, '', 'tendernet.kz@mail.com',
              [EMAIL_MANAGER], html_message=message, fail_silently=False)
    return JsonResponse(return_dict)


# Pko iso и т.д

def pko(request):
    sub = forms.Pko()
    if request.method == 'POST':

        sub = forms.Pko(request.POST)
        subject = 'ПКО с сайта Tendernet.kz'
        notify_admin_service.delay(sub.data, subject)
        messages.add_message(request, messages.SUCCESS, 'Ваша заявка принята! В ближайшее время с вами свяжется менеджер.')
        return redirect('pko')
    return render(request, 'pko.html', {'form': sub})



def iso(request):
    sub = forms.Iso()
    if request.method == 'POST':
        sub = forms.Iso(request.POST)
        subject = 'ПКО с сайта Tendernet.kz'
        notify_admin_service.delay(sub.data, subject)
        messages.add_message(request, messages.SUCCESS, 'Ваша заявка принята! В ближайшее время с вами свяжется менеджер.')
        return redirect('iso')
    return render(request, 'iso.html', {'form': sub})


def legal(request):
    sub = forms.Iso()
    if request.method == 'POST':

        sub = forms.Iso(request.POST)
        notify_admin_service.delay(sub.data, 'legal')
        messages.add_message(request, messages.SUCCESS, 'Ваша заявка принята! В ближайшее время с вами свяжется менеджер.')
        return redirect('legal')
    return render(request, 'legal.html', {'form': sub})


def outsourcing(request):
    sub = forms.Iso()
    if request.metthod == 'POST':

        sub = forms.Iso(request.POST)
        notify_admin_service.delay(sub.data, 'outsourcing')
        messages.add_message(request, messages.SUCCESS, 'Ваша заявка принята! В ближайшее время с вами свяжется менеджер.')
        return redirect('outsourching')
    return render(request, 'outsourcing.html', {'form': sub})
