from django.db import models


class SavegameManager(models.Manager):
    SAVEGAME_SESSION_KEY = 'savegame_id'

    @staticmethod
    def get_from_session(request):
        return request.session.get(SavegameManager.SAVEGAME_SESSION_KEY, None)

    @staticmethod
    def set_to_session(request, savegame_id):
        request.session[SavegameManager.SAVEGAME_SESSION_KEY] = savegame_id


class SavegameBasedObjectManager(models.Manager):
    def get_visible(self, request=None, savegame=None):
        if request:
            return self.filter(savegame=SavegameManager.get_from_session(request))
        if savegame:
            return self.filter(savegame=savegame)
        else:
            raise AttributeError('Function called with neither request nor savegame.')
