from django.contrib import admin
from .models import Profile, Price 

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'dob')

admin.site.register(Profile)

class PriceAdmin(admin.ModelAdmin):
    list_display = ('name')

admin.site.register(Price)