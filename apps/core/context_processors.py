from apps.account.models import Savegame


def current_savegame(request):
    savegame_id = request.session['savegame_id']
    return {
        'savegame_id': savegame_id
    }
