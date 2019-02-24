from django.shortcuts import redirect
from django.urls import reverse

from apps.account.managers import SavegameManager
from apps.military.models import Battle


class RedirectToActiveBattleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        if '/admin/' not in request.path:
            savegame = SavegameManager.get_from_session(request)

            if request.path != reverse('military:battle-view') and \
                    'military/battle/execute-action/' not in request.path and \
                    Battle.objects.get_visible(savegame=savegame).filter(done=False).exists():
                return redirect('military:battle-view')

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
