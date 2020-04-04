from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
# pages/views.py
from django.views.generic import TemplateView
from lots.models import Article
from . import views
from django.contrib import messages
from django.http import HttpResponseRedirect

from lots.models import Article

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from lots.filters import ArticleFilter

from django.shortcuts import render, redirect


from . import forms
from django.core.mail import send_mail
from tn_first.settings import EMAIL_HOST_USER
from django.urls import reverse


def index(request):
    bbs = Article.objects.order_by('-published_at')

    myHomeFilter = ArticleFilter(request.GET, queryset=Article.objects.all())
    bbs = myHomeFilter.qs

    paginator = Paginator(bbs, 10)
    page = request.GET.get('page')
    try:
        bbs = paginator.page(page)
    except PageNotAnInteger:
        bbs = paginator.page(1)
    except EmptyPage:
        bbs = paginator.page(paginator.num_pages)

    context = {'bbs': bbs, 'myHomeFilter': myHomeFilter}
    return render(request, 'index.html', context)


def modal(request):
    sub = forms.BookForm()
    if request.method == 'POST':
        sub = forms.BookForm(request.POST)
        subject = sub['name'].value()
        message = sub['nomer'].value()
        recepient = 'askar9315@gmail.com'
        send_mail(subject, message, EMAIL_HOST_USER, [recepient], fail_silently=False)
        return HttpResponseRedirect('index')
    return render(request, 'blocks/modal.html', {'form': sub})
