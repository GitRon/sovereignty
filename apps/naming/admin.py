from django.contrib import admin

from apps.naming.models import LocationNameSuffix, PersonName, LocationNamePrefix


@admin.register(PersonName)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ['name', 'gender']


admin.site.register(LocationNamePrefix)
admin.site.register(LocationNameSuffix)
