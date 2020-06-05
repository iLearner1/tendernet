from django.contrib import admin

from .models import Article, FavoriteSearch
from lots.models import Cities, Regions, LotFile


class LotFileAdmin(admin.StackedInline):
    model = LotFile

admin.site.register(LotFile)

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'customer','city','numb','price','statzakup',  'date','yst',)
    prepopulated_fields = {'slug': ('title',)} # new
    autocomplete_fields = ["city", "region"]
    inlines = [LotFileAdmin]
    list_per_page = 30
    exclude = ('favourite',)

    class Media:
        css = {
            'all': ('css/admin-styles.css',)
        }


class CitiesAdmin(admin.ModelAdmin):
    ordering = ["name"]
    search_fields = ["name"]


class RegionsAdmin(admin.ModelAdmin):
    ordering = ["name"]
    search_fields = ["name"]


admin.site.register(Article, ArticleAdmin)
admin.site.register(Cities, CitiesAdmin)
admin.site.register(Regions, RegionsAdmin)




admin.site.register(FavoriteSearch)