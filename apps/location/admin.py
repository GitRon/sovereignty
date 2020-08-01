from django.contrib import admin

from apps.location.models import County, Map

admin.site.register(Map)


@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ('name', 'savegame')
    list_filter = ('savegame',)
    search_fields = ('name',)
