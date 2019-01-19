from apps.account.managers import SavegameManager
from apps.account.models import Savegame


def current_savegame(request):
    savegame_id = SavegameManager.get_from_session(request)

    savegame = None
    if savegame_id:
        savegame = Savegame.objects.get(id=savegame_id)

    return  {
        'savegame_id': savegame_id,
        'savegame': savegame,
    }
