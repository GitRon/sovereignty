from django.contrib import messages
from django.views import generic

from apps.account.models import Savegame


class Dashboard(generic.TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # todo add data

        return context


class Menu(generic.TemplateView):
    template_name = 'menu.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # List logic
        context['savegame_list'] = Savegame.objects.order_by('-created_at')

        # Loading logic
        context['savegame_loaded'] = False
        if self.kwargs.get('savegame_id', None):
            # Store ID in session
            self.request.session['savegame_id'] = self.kwargs['savegame_id']
            messages.add_message(self.request, messages.SUCCESS, 'Savegame successfully loaded.')
            context['savegame_loaded'] = True

        return context
