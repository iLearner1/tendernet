from django.contrib import messages

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from zakaz.models import Zakaz, Zakazdoc
from django.views import View
from . import forms
from django.core.mail import send_mail
from tn_first.settings import EMAIL_HOST_USER

def basket_adding_lot(request):
    return_dict = dict()
    print(request.POST)
    data = request.POST
    product_id1 = data.get("product_id1")
    user_id1 = data.get("user_id1")
    new_product = Zakaz.objects.get_or_create(lot_id=product_id1, klyent_id=user_id1,)
    return JsonResponse(return_dict)


def basket_adding_doc(request):
    return_dict = dict()
    print(request.POST)
    data = request.POST
    product_id = data.get("product_id")
    user_id = data.get("user_id")
    new_product = Zakazdoc.objects.get_or_create(lots_id=product_id, klyenty_id=user_id,)
    return JsonResponse(return_dict)


# Pko iso и т.д

def pko(request):
    sub = forms.Pko()
    if request.method == 'POST':
        sub = forms.Pko(request.POST)
        subject = 'ПКО с сайта Tendernet.kz'
        message = str(sub['field'].value())
        recepient = 'askar9315@gmail.com'
        send_mail(subject,
            message, EMAIL_HOST_USER, [recepient], fail_silently = False)
        return render(request, 'success.html', {'recepient': recepient})
    return render(request, 'pko.html', {'form':sub})

def iso(request):
    sub = forms.Iso()
    if request.method == 'POST':
        sub = forms.Iso(request.POST)
        subject = 'ПКО с сайта Tendernet.kz'
        message = sub['field'].value()
        recepient = 'askar9315@gmail.com'
        send_mail(subject,
            message, EMAIL_HOST_USER, [recepient], fail_silently = False)
        return render(request, 'success.html', {'recepient': recepient})
    return render(request, 'iso.html', {'form':sub})

