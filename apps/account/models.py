import random

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.defaultfilters import date

from apps.account.managers import SavegameManager


class Savegame(models.Model):
    from apps.dynasty.models import Dynasty

    DEFAULT_STARTING_YEAR = 800

    created_at = models.DateTimeField(auto_now_add=True)
    current_year = models.PositiveIntegerField(default=DEFAULT_STARTING_YEAR)
    playing_as = models.OneToOneField(Dynasty, related_name='playing_in_savegame', null=True, blank=True,
                                      on_delete=models.CASCADE)

    objects = SavegameManager()

    def __str__(self):
        date_str = date(self.created_at, 'd.m.Y H:i')
        return f'#{self.id} - {date_str}'


@receiver(pre_save, sender=Savegame, dispatch_uid="savegame.set_current_year")
def set_current_year(sender, instance, **kwargs):
    if not instance.current_year:
        instance.current_year = random.randrange(Savegame.DEFAULT_STARTING_YEAR * 0.9,
                                                 Savegame.DEFAULT_STARTING_YEAR * 1.1)
