"""tn_first URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users.forms import EmailValidationOnForgotPassword, CustomEmailValidationOnForgotPassword
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView

from users import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('lots/', include('lots.urls')),
    path('', include('home.urls')),
    path('', include('zakaz.urls')),
    path('accounts/login/', views.LoginView.as_view(), name='login'),
    path('accounts/reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(form_class=CustomEmailValidationOnForgotPassword), name='password_reset_confirm'),
    path('accounts/password_reset/', PasswordResetView.as_view(form_class=EmailValidationOnForgotPassword), name='password_reset'),
    path('accounts/', include('django.contrib.auth.urls')),

    path('login/home/', views.index),

    path('signup/', views.signup, name='register'),
    path('activate/<uidb64>/<token>/', views.Activate.as_view(), name='activate'),
    path('activate/', views.Activate.as_view(), name='activate'),

    path('edit_profile/', views.edit_profile, name="edit_profile"),
    path('profile/', views.profile, name="profile"),
    path('tariff/', views.tariff, name="tariff"),
    path('schedule_tariff_change_email/', views.schedule_tariff_change_email, name="schedule_tariff_change_email"),
    path('edit_tarif/', views.edit_tarif, name="edit_tarif"),
    path('basket_list/', views.basket_list, name="basket_list"),
    path('history_list/', views.history_list, name="history_list"),
    path('send_user_info_to_manager', views.send_user_info_to_manager, name='send_info_to_manager')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
