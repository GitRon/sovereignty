from apps.account.managers import SavegameManager


def current_savegame(request):
    return {
        'savegame_id': SavegameManager.get_from_session(request)
    }
