from django.contrib import admin

from apps.location.models import County, Map

admin.site.register(County)
admin.site.register(Map)
