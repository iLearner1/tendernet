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
from users import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('lots/', include('lots.urls')), # new
    path('', include('home.urls')),
    path('', include('zakaz.urls')),

    path('', include('django.contrib.auth.urls')),
    path('login/home/', views.index),
    #path('login/', views.user_login, name="user_login"),
    #path('logout/', views.user_logout, name="user_logout"),
    path('register/', views.register, name="register"),
    path('edit_profile/', views.edit_profile, name="edit_profile"),
    path('profile/', views.profile, name="profile"),
    path('edit_tarif/', views.edit_tarif, name="edit_tarif"),
    path('basket_list/', views.basket_list, name="basket_list"),
    path('history_list/', views.history_list, name="history_list"),




]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
