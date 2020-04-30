# pages/urls.py
from django.urls import path
from home import views

from .views import index

urlpatterns = [
    path('', index, name='index'),
    path('contact/', views.contact, name='contact'),
    path('modal/', views.modal, name='modal'),
    path('sp-push-worker-fb.js/', views.sp_push_worker_fb_js, name='sp_push_worker_fb_js'),
    path('sp-push-manifest.json/', views.sp_push_manifest_json, name='sp_push_manifest_json'),
]
