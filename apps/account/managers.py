import random

from django.db import models


class SavegameManager(models.Manager):

    def get_from_session(self, request):
        if request.session['savegame_id']:
            return self.get(id=request.session['savegame_id'])
        return None
