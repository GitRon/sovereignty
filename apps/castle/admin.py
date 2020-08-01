from django.contrib import admin

from apps.castle.models import CastleUpgrade, Castle

admin.site.register(Castle)


@admin.register(CastleUpgrade)
class CastleUpgradeAdmin(admin.ModelAdmin):
    list_display = ('name', 'building_cost', 'maintenance_cost', 'defense_bonus')
