from django.contrib import admin

from .models import Article, FavoriteSearch
from lots.models import Cities

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'customer','city','numb','price','statzakup',  'date','yst','down',)
    prepopulated_fields = {'slug': ('title',)} # new
    list_per_page = 30

    class Media:
        css = {
            'all': ('css/admin-styles.css',)
        }

admin.site.register(Article, ArticleAdmin)
admin.site.register(Cities)

admin.site.register(FavoriteSearch);