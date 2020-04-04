from django.urls import path, include
from zakaz import views

urlpatterns = [
    path('basket_adding_lot/', views.basket_adding_lot, name="basket_adding_lot"),
    path('basket_adding_doc/', views.basket_adding_doc, name="basket_adding_doc"),
    path('pko/', views.pko, name="pko"),
    path('iso/', views.iso, name="iso"),


]