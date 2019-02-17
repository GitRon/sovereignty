from django.contrib import admin

from apps.military.models import Regiment, RegimentType, RegimentUpgrade, Battle, BattlefieldTile

admin.site.register(Regiment)
admin.site.register(RegimentType)
admin.site.register(RegimentUpgrade)
admin.site.register(Battle)
admin.site.register(BattlefieldTile)
