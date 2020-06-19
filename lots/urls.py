from django.urls import path
from . import views

urlpatterns = [
    path("<int:ID>/favourite_post/", views.favourite_post, name="favourite_post"),
    path("<int:ID>/favourite_post_ajax/", views.favourite_post_ajax, name="favourite_post_ajax"),
    path("", views.post_list, name="post_list"),
    path("api_interface", views.api_interface, name="api_interface"),
    path("insert_regions_locations", views.insert_regions_locations, name="insert_regions_locations"),
    path("region_change_ajax", views.region_change_ajax, name="region_change_ajax"),
    path("delete_lots", views.delete_lots, name="delete_lots"),
    path("<int:id>/<slug:slug>/", views.post_detail, name="post_detail"),
    path("<int:id>/<slug:slug>/delete/", views.post_delete, name="post_delete"),
    path("favourites/", views.post_favourite_list, name="post_favourite_list"),
    path("searches/", views.post_search, name="post_search"),
    path("favorite/search", views.save_favorite_search, name="save_favorite_search"),
    path(
        "favorite/search/list", views.favorite_search_list, name="favorite_search_list"
    ),
    path(
        "remove/favorite/search/<int:id>",
        views.remove_favorite_search,
        name="remove_favorite_search",
    ),
    path("archived", views.archived_post, name="archived_post"),
]
