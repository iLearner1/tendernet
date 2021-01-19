import os

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404

# pages/views.py
from django.views.generic import TemplateView
from lots.models import Article, Cities
from . import views
from django.contrib import messages
from django.http import HttpResponseRedirect
from lots.models import Article
from zakaz.models import Zakaz
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from lots.filters import ArticleFilter
from django.shortcuts import render, redirect
from . import forms
from django.core.mail import send_mail
from tn_first.settings import CONTACT_MAIL_RECEIVER, EMAIL_MANAGER
from django.urls import reverse
from lots.utils.Choices import PURCHASE_METHOD_CHOICES as ZAKUP_CHOICES, SUBJECT_OF_PURCHASE_CHOICES as PURCHASE_CHOICES
from django.utils import timezone
from .tasks import send_query, send_consultation_query
from tn_first import settings as tn_first_settings
from django.template.loader import render_to_string

def index(request):
    myHomeFilter = ArticleFilter(
        request.GET, queryset=Article.objects.filter(date__gt=timezone.now())
    )
    cities = Cities.objects.all()
    bbs = myHomeFilter.qs
    all_zakaz = Zakaz.objects.all()
    paginator = Paginator(bbs, 10)
    page = request.GET.get("page")
    try:
        bbs = paginator.page(page)
    except PageNotAnInteger:
        bbs = paginator.page(1)
    except EmptyPage:
        bbs = paginator.page(paginator.num_pages)

    paginator = Paginator(all_zakaz, 25)
    page_number = request.GET.get("page", 1)
    all_zakaz = paginator.page(page_number)
    total_posts = paginator.num_pages

    context = {
        "bbs": bbs,
        "myHomeFilter": myHomeFilter,
        "cities": cities,
        "PURCHASE_METHOD_CHOICES": ZAKUP_CHOICES,
        "SUBJECT_OF_PURCHASE_CHOICES": PURCHASE_CHOICES,
        'all_zakaz': all_zakaz,
        'total_posts': total_posts
    }

    if(request.is_ajax()):
        return render(request, 'blocks/home-page-zakaz-list.html', context)

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


def send_consultaion_query(request):
    user = 'Anymouse'
    if request.method == "POST":
        if request.user.is_authenticated:
            user = request.user.username
        # send_consultation_query.delay(
        #     request.POST.get('name'), request.POST.get('number'), user)

        html = render_to_string('blocks/consultation-mail.html',
                            {'name': request.POST.get('name'), 'phone': request.POST.get('number'), 'comment': request.POST.get('comment'), 'user': user})
        send_mail('consultation/query', '', 'tendernet.kz@mail.com',
              [EMAIL_MANAGER, 'tendernetkz@mail.ru', 'mdmotailab@gmail.com'], html_message=html, fail_silently=False)

        return redirect('index')


def sp_push_worker_fb_js(request):
    file_path = tn_first_settings.BASE_DIR + '/static/js/sp-push-worker-fb.js'
    file_content = open(file_path, "rb")
    return HttpResponse(file_content)


def sp_push_manifest_json(request):
    file_path = tn_first_settings.BASE_DIR + '/static/json/sp-push-manifest.json'
    file_content = open(file_path, "rb")
    return HttpResponse(file_content)
