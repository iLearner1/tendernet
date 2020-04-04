from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import Profile
from lots.models import Article
from django.contrib import messages


# Create your views here.
def index(request):#создаем свою функцию
    context = {}#с помощью словаря можем передать модель и форму в шаблон HTML
    return render(request, 'index.html', context)#собственно вызываем шаблон HTML



def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    if 'next'in  request.POST:
                        return redirect(request.POST.get('next'))
                    return HttpResponseRedirect(request.POST.get('next'))
                else:
                    messages.warning(request, 'Пользователь не активирован')
            else:
                messages.warning(request, 'Пользователь не найден')
    else:
        form = UserLoginForm()

    context = {
        'form': form,

    }
    return render(request, 'login.html', context)

def user_logout(request):
    logout(request)
    return redirect('index')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST or None)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            Profile.objects.create(user=new_user)
            if 'next'in  request.POST:
                return redirect(request.POST.get('next'))            
            return redirect(request.POST.get('next'))
    else:
        form = UserRegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'register.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserEditForm(data=request.POST or None, instance=request.user)
        profile_form = ProfileEditForm(data=request.POST or None, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            
            user_form.save()
            profile_form.save()
            
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'edit_profile.html', context)

def profile(request):
    user = request.user
    basket_posts = user.klyent.all()
    context = {
        'basket_posts': basket_posts,

    }

    return render(request, 'profile.html', context)


def edit_tarif(request):
    if request.method == 'POST':
        tarif_form = TarifEditForm(data=request.POST or None, instance=request.user.profile)
        if tarif_form.is_valid():
            tarif_form.save()

    else:
        tarif_form = TarifEditForm(instance=request.user.profile)

    context = {
        'tarif_form': tarif_form,
    }
    return render(request, 'edit_tarif.html', context)

def basket_list(request):
    basket_list = Article.objects.all()
    user = request.user
    basket_posts = user.klyent.all()
    context = {
        'basket_posts': basket_posts,
        'basket_list': basket_list,
    }
    return render(request, 'basket_list.html', context)



def history_list(request):

    user = request.user
    history_list = user.klyent.all()

    context = {
        'history_list': history_list,

    }
    return render(request, 'history_list.html', context)