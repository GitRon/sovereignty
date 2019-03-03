from django.contrib import admin

from apps.military.models import Regiment, RegimentType, RegimentUpgrade, Battle, BattlefieldTile, BattleLogEntry


@admin.register(Regiment)
class RegimentAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'county', 'get_savegame', 'current_men')
    search_fields = ['name', 'county__name']

    def get_savegame(self, obj):
        return obj.county.savegame

    get_savegame.short_description = 'Savegame'
    get_savegame.admin_order_field = 'county__savegame'


admin.site.register(RegimentType)
admin.site.register(RegimentUpgrade)
admin.site.register(Battle)
admin.site.register(BattleLogEntry)
admin.site.register(BattlefieldTile)
