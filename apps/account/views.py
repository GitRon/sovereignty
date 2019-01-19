from django.contrib import messages
from django.views import generic

from apps.account.managers import SavegameManager
from apps.account.models import Savegame
from apps.account.services import FinishYearService
from apps.messaging.models import EventMessage


class Dashboard(generic.TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['event_messages'] = EventMessage.objects.get_visible(request=self.request).get_open()
        context['message_type_ok'] = EventMessage.TYPE_OK
        context['message_type_yesno'] = EventMessage.TYPE_YES_NO

        return context


class Menu(generic.TemplateView):
    template_name = 'menu.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # List logic
        context['savegame_list'] = Savegame.objects.order_by('-created_at')

        # Loading logic
        context['savegame_loaded'] = False
        if self.kwargs.get(SavegameManager.SAVEGAME_SESSION_KEY, None):
            # Store ID in session
            SavegameManager.set_to_session(self.request, self.kwargs[SavegameManager.SAVEGAME_SESSION_KEY])
            messages.add_message(self.request, messages.SUCCESS, 'Savegame successfully loaded.')
            context['savegame_loaded'] = True

        return context


class FinishYear(generic.RedirectView):
    pattern_name = 'account:dashboard-view'

    def get(self, request, *args, **kwargs):

        # Get current savegame
        savegame_id = SavegameManager.get_from_session(request)

        # Finish year
        fys = FinishYearService(savegame_id)
        fys.process()

        return super().get(request, *args, **kwargs)

