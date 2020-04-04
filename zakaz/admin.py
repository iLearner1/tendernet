from django.contrib import admin

from zakaz.models import Zakaz, Zakazdoc


class ZakazAdmin(admin.ModelAdmin):
    list_display = ('date','status','klyent','lot','zavdate',)


admin.site.register(Zakaz, ZakazAdmin)

class ZakazdocAdmin(admin.ModelAdmin):
    list_display = ('daty','status','klyenty','lots',)


admin.site.register(Zakazdoc, ZakazdocAdmin)