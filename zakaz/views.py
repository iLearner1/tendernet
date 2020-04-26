from django.contrib import messages

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from zakaz.models import Zakaz, Zakazdoc
from django.views import View
from . import forms
from .tasks import notify_admin_service


def basket_adding_lot(request):
    return_dict = dict()
    print(request.POST)
    data = request.POST
    product_id1 = data.get("product_id1")
    user_id1 = data.get("user_id1")
    new_product = Zakaz.objects.get_or_create(
        lot_id=product_id1, klyent_id=user_id1,)
    return JsonResponse(return_dict)


def basket_adding_doc(request):
    return_dict = dict()
    print(request.POST)
    data = request.POST
    product_id = data.get("product_id")
    user_id = data.get("user_id")
    new_product = Zakazdoc.objects.get_or_create(
        lots_id=product_id, klyenty_id=user_id,)
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
