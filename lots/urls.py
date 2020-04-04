from django.urls import path
from . import views

urlpatterns = [

    path('<slug:slug>/favourite_post/', views.favourite_post, name="favourite_post"),
    path('', views.post_list, name="post_list"),
    path('<int:id>/<slug:slug>/', views.post_detail, name="post_detail"),
    path('favourites/', views.post_favourite_list, name="post_favourite_list"),
]


