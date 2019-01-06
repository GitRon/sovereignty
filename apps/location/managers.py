from random import randint

from django.db import models

from apps.account.managers import SavegameBasedObjectManager
from apps.core.managers import RandomManager


class CountyManager(SavegameBasedObjectManager):
    pass


class MapDotManager(RandomManager):
    pass
