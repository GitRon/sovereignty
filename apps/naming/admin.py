from django.contrib import admin

from apps.naming.models import LocationNamePostfix, PersonName, LocationNamePrefix

admin.site.register(PersonName)
admin.site.register(LocationNamePrefix)
admin.site.register(LocationNamePostfix)
