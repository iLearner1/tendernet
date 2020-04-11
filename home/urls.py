# pages/urls.py
from django.urls import path
from home import views

from .views import index

urlpatterns = [
    path('', index, name='index'),
    path('modal/', views.modal, name='modal'),
]
