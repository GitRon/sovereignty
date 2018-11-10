from django.contrib import admin

from apps.naming.models import PersonNamePrefix, PersonNamePostfix

admin.site.register(PersonNamePrefix)
admin.site.register(PersonNamePostfix)
