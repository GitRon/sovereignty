from django.db import models
from django.template.defaultfilters import date

from apps.account.managers import SavegameManager


class Savegame(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    objects = SavegameManager()

    def __str__(self):
        date_str = date(self.created_at, 'd.m.Y H:i')
        return f'#{self.id} - {date_str}'
