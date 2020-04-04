from django.contrib import admin

from .models import Article
from lots.models import Cities

class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'body','city','numb','price','statzakup', 'date','yst','down',)
    prepopulated_fields = {'slug': ('title',)} # new

admin.site.register(Article, ArticleAdmin)
admin.site.register(Cities)