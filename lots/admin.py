from django.contrib import admin
from django import forms
from .models import Article, FavoriteSearch
from lots.models import Cities, Regions, Unit


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = '__all__'
        exclude = ('numb','favourite')
        labels = {
            'id': 'Lot orignal number',
        }

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'customer','city','id','price','statzakup',  'date','yst',)
    prepopulated_fields = {'slug': ('title',)} # new
    autocomplete_fields = ["city", "region"]
    ordering = ['-id']
    list_per_page = 500
    readonly_fields = ('id',)
    # exclude = ('favourite',)
    form = ArticleForm
    class Media:
        css = { 'all': ('css/admin-styles.css',) }
        js = ('admin/js/custom-js.js',)


class UnitAdmin(admin.ModelAdmin):
    ordering = ["name"]
    search_fields = ["name"]

class CitiesAdmin(admin.ModelAdmin):
    ordering = ["name"]
    search_fields = ["name"]


class RegionsAdmin(admin.ModelAdmin):
    ordering = ["name"]
    search_fields = ["name"]


admin.site.register(Article, ArticleAdmin)
admin.site.register(Cities, CitiesAdmin)
admin.site.register(Regions, RegionsAdmin)
admin.site.register(Unit, UnitAdmin)




admin.site.register(FavoriteSearch)