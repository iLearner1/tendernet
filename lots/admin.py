from django.contrib import admin

from .models import Article, FavoriteSearch
from lots.models import Cities

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'body','city','numb','price','statzakup', 'purchase_method', 'date','yst','down',)
    prepopulated_fields = {'slug': ('title',)} # new

admin.site.register(Article, ArticleAdmin)
admin.site.register(Cities)

admin.site.register(FavoriteSearch);