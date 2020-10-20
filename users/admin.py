from django.contrib import admin
from django import forms
from .models import Profile, Price 


class ProfileAdminForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
        exclude = ['tarif_expire_date']


class ProfileAdmin(admin.ModelAdmin):
    # list_display = ('user', 'dob')
    # form = ProfileAdminForm
    pass


class PriceAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(Profile)
admin.site.register(Price)
