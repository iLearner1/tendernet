# Create your views here.
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from users.forms import SignupForm, ProfileEditForm, UserEditForm, TarifEditForm, LoginForm, PasswordResetForm
from users.models import Profile
from lots.models import Article
from tn_first.settings import EMAIL_MANAGER
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from users.tasks import task_tariff_change_email, send_mail_to_manager
import datetime
from django.utils import timezone
from users.models import Price
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import MultipleObjectsReturned


def index(request):  # создаем свою функцию
    context = {}  # с помощью словаря можем передать модель и форму в шаблон HTML
    return render(request, 'index.html', context)  # собственно вызываем шаблон HTML


def find_user_by_email(email):
    user = None
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return None

    return user


def find_user_by_username(username):
    user = None
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None
    return user


def authenticate_user(user_or_email):
    user = find_user_by_email(user_or_email)

    if user is None:
        user = find_user_by_username(user_or_email)

    return user


def check_pass(user, password):
    if user is None:
        return user
    else:
        if user.check_password(password):
            return user

    return None


class LoginView(View):

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/lots')

        form = LoginForm()
        return render(request, "registration/login.html", {"form": form})


    def post(self, request):
        if request.user.is_authenticated:
            return redirect('/lots')
        
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate_user(username)

        if user is not None:
            user = check_pass(user, password)

        context = {}

        if user is not None:
            if user.is_active:
                login(request, user)
                if 'next' in request.POST and len(request.POST.get('next')) > 0:
                    return redirect(self.request.POST.get('next', '/'))
                else:
                    return redirect(request.GET.get('next', '/'))
            else:
                context['error_message'] = "user is not active"
        else:
            context['error_message'] = "email or password not correct"

        context['form'] = LoginForm()
        return render(request, 'registration/login.html', context)

def signup(request):

    if request.user.is_authenticated:
        return redirect('/lots')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.set_password(request.POST.get('password'))
            user.save()
           
            # check if free tariff exists
            # if not exist then create
            price, created = Price.objects.get_or_create(name='MN12')
            try:
                if price:
                    user_profile= Profile(
                        user=user, 
                        tarif_id=price.id,
                        company_name=request.POST.get('company_name', ''),
                        company_business_number=request.POST.get("company_business_number", ''))
                    user_profile.save()
            except Exception as e:
                return redirect('/lots?error='+str(e))
                
            current_site = get_current_site(request)
            scheme = 'http://'
            if request.is_secure():
                scheme = 'https://'

            mail_subject = 'Активируйте пожалуйста Ваш аккаунт на tendernet.kz'
            message = render_to_string('acc_active_email.html', {
                'scheme': scheme,
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })

            to_email = form.cleaned_data.get('email')

            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            mail_subject = 'новый пользователь активировал электронную почту'
            message = render_to_string('new_user_registration_email_to_manager.html', {
                'username': username,
                'email': email,
            })
            email = EmailMessage(
                mail_subject, message, to=[EMAIL_MANAGER]
            )
            email.send()

            return render(request, 'confirm_registration.html')
    else:
        form = SignupForm()
    return render(request, "register.html", {'form': form})


class Activate(View):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            
            return render(request, 'email_activate.html')
        else:
            return HttpResponse('Ссылка на активации недействительна!')


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
    if not request.user.is_authenticated:
        return redirect(reverse('login')+'?next=/profile/?user_id=5/')

    current_user = None 
    if request.GET.get('user_id'):
        current_user = get_object_or_404(User, id=request.GET.get('user_id'))
    else:
        current_user = request.user
    
    basket_posts = current_user.klyent.all()
    context = {
        'basket_posts': basket_posts,
        'current_user':current_user
    }

    return render(request, 'profile.html', context)


def tariff(request):
    return render(request, "tariff.html")


@csrf_exempt
def schedule_tariff_change_email(request):
    tariff_id = request.POST.get('id')
    current_tariff = None
    change_tariff = None
    days = {
        'MN12': 365,
        'MN6':  182,
        'MN3':  91,
        'MN1':  31,
        'EXP_MN12':  365,
        'EXP_MN6':  182,
        'EXP_MN3':  91,
        'EXP_MN1':  31,
    }
    try:
        profile = Profile.objects.filter(user=request.user)
        current_tariff = profile[0].tarif.name

        user_email = profile[0].user.email
        price = Price.objects.filter(id=tariff_id)
        change_tariff = price[0].name

        profile[0].tarif_expire_date = timezone.now() + timezone.timedelta(days=days[change_tariff])
        profile[0].save()

    except Exception as e:
        print("exception in finding user/tariff")


    if current_tariff != None and change_tariff != None and change_tariff != "free":
        #changing expire date of tarif
        task_tariff_change_email.apply_async(args=[user_email, change_tariff])
        task_tariff_change_email.apply_async(args=[user_email, change_tariff], eta=datetime.datetime.now() + datetime.timedelta(days=3))

    return HttpResponse(200)


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

@login_required
def basket_list(request):
    basket_list = Article.objects.all()
    user = request.user
    basket_posts = user.klyent.all()

    paginator = Paginator(basket_posts, 25)
    page_number = request.GET.get("page", 1)
    basket_posts = paginator.page(page_number)
    total_posts = paginator.count

    context = {
        'basket_posts': basket_posts,
        'basket_list': basket_list,
        'total_posts': total_posts,
        "total_pages": paginator.num_pages,
    }

    if(request.is_ajax()):
        print("this is ajax request");
        return render(request, 'blocks/basket-list-partials.html', context)

    
    return render(request, 'basket_list.html', context)


def history_list(request):
    user = request.user
    history_list = user.klyent.all()

    context = {
        'history_list': history_list,

    }
    return render(request, 'history_list.html', context)

def send_user_info_to_manager(request):
    # this function will send mail to manager with user info
    # if user authenticated
    send_mail_to_manager.apply_async(args=[request.user.username, request.user.email])
    return HttpResponse(200)
