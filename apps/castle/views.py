from django.views import generic

from apps.account.managers import SavegameManager
from apps.account.models import Savegame
from apps.castle.models import CastleUpgrade, Castle


class CastleOverviewView(generic.TemplateView):
    template_name = 'castle_overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        savegame = Savegame.objects.get(pk=SavegameManager.get_from_session(self.request))
        context['dynasty'] = savegame.playing_as

        context['castle'], _ = Castle.objects.get_or_create(county=savegame.playing_as.home_county, savegame=savegame)
        context['castle_upgrade_list'] = CastleUpgrade.objects.all()
        return context
