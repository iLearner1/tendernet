from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404

# pages/views.py
from django.views.generic import TemplateView
from lots.models import Article, Cities
from . import views
from django.contrib import messages
from django.http import HttpResponseRedirect
from lots.models import Article
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from lots.filters import ArticleFilter
from django.shortcuts import render, redirect
from . import forms
from django.core.mail import send_mail
from tn_first.settings import CONTACT_MAIL_RECEIVER
from django.urls import reverse
from lots.utils.Choices import ZAKUP_CHOICES, PURCHASE_CHOICES
from django.utils import timezone
from .tasks import send_query, send_consultation_query


def index(request):
    myHomeFilter = ArticleFilter(
        request.GET, queryset=Article.objects.filter(date__gt=timezone.now())
    )
    cities = Cities.objects.all()
    bbs = myHomeFilter.qs

    paginator = Paginator(bbs, 10)
    page = request.GET.get("page")
    try:
        bbs = paginator.page(page)
    except PageNotAnInteger:
        bbs = paginator.page(1)
    except EmptyPage:
        bbs = paginator.page(paginator.num_pages)

    context = {
        "bbs": bbs,
        "myHomeFilter": myHomeFilter,
        "cities": cities,
        "ZAKUP_CHOICES": ZAKUP_CHOICES,
        "PURCHASE_CHOICES": PURCHASE_CHOICES,
    }
    print(request.user.is_authenticated)
    return render(request, "index.html", context)


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        user = 'Anymouse'
        if request.user.is_authenticated:
            user = request.user.username

        if (not name) and (not email) and (not message):
            return redirect(request.META.get('HTTP_REFERER'))
        send_query.delay(name, email, message)
        messages.add_message(request, messages.SUCCESS,
                             'Successfully sent your query to our team, we will contact with you soon')
        return redirect('index')

    return render(request, 'contact-page.html')


def modal(request):
    user = 'Anymouse'
    if request.method == "POST":
        if request.user.is_authenticated:
            user = request.user.username
        send_consultation_query.delay(
            request.POST.get('name'), request.POST.get('number'), user)
        return redirect('index')
