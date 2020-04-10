from django.urls import path
from . import views

urlpatterns = [

    path('<slug:slug>/favourite_post/', views.favourite_post, name="favourite_post"),
    path('', views.post_list, name="post_list"),
    path('<int:id>/<slug:slug>/', views.post_detail, name="post_detail"),
    path('<int:id>/<slug:slug>/delete/', views.post_delete, name="post_delete"),
    path('favourites/', views.post_favourite_list, name="post_favourite_list"),
    path('searches/', views.post_search, name='post_search'),
    path("favorite/search", views.save_favorite_search, name="save_favorite_search"),
    path("favorite/serach/list", views.favorite_search_list, name="favorite_search_list"),
    path("remove/favorite/search/<int:id>", views.remove_favorite_search, name="remove_favorite_search")
]


