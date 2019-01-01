def current_savegame(request):
    return {
        'savegame_id': request.session['savegame_id']
    }
