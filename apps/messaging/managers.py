from django.db import models

from apps.account.managers import SavegameBasedObjectManager


class MessageQuerySet(models.QuerySet):
    def get_open(self):
        return self.filter(done=False)


class MessageManager(SavegameBasedObjectManager):

    def get_queryset(self):
        return MessageQuerySet(self.model, using=self._db)  # Important!

    def get_open(self):
        return self.get_queryset().get_open()
