from django.contrib import admin

from apps.dynasty.models import Person, Trait

admin.site.register(Person)
admin.site.register(Trait)
