from apps.account.managers import SavegameBasedObjectManager


class BattlefieldTileManager(SavegameBasedObjectManager):
    pass


class BattleManager(SavegameBasedObjectManager):

    def get_current_battle(self, request=None, savegame=None):
        return self.get_visible(request, savegame).filter(done=False).first()
