from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import generic

from apps.account.managers import SavegameManager
from apps.account.models import Savegame
from apps.military.models import Regiment, RegimentType
from apps.military.services.battlefield import BattlefieldService
from apps.military.services.regiment_actions import RegimentActionService


class OverviewView(generic.TemplateView):
    template_name = 'overview.html'


class RegimentDetailView(generic.DetailView):
    model = Regiment
    template_name = 'regiment_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upgradable_regiment_types'] = RegimentType.objects.exclude(id=self.object.type.id)
        return context


class RegimentTrainingView(generic.TemplateView):
    template_name = 'regiment_detail.html'
    model = Regiment
    regiment = None
    regiment_type = None

    def get(self, request, *args, **kwargs):
        savegame = Savegame.objects.get(pk=SavegameManager.get_from_session(self.request))
        self.regiment = get_object_or_404(Regiment, pk=self.kwargs.pop('pk'), county__savegame=savegame)
        self.regiment_type = get_object_or_404(RegimentType, pk=self.kwargs.pop('type_id'))

        self.regiment.type = self.regiment_type
        self.regiment.save()

        messages.add_message(self.request, messages.SUCCESS, f'Regiment successfully trained to {self.regiment_type}.')

        return redirect(reverse('military:regiment-detail-view', args=[self.regiment.id]))


class BattleView(generic.TemplateView):
    template_name = 'battle.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        savegame = Savegame.objects.get(pk=Savegame.objects.get_from_session(self.request))
        bs = BattlefieldService(savegame)
        context['battle_data'] = bs.get_current_battlefield()
        # todo for now all your regiments are fighting
        context['my_regiments'] = savegame.current_county.regiments.all

        # Constants
        context['ba_move_left'] = RegimentActionService.ACTION_MOVE_LEFT
        context['ba_move_right'] = RegimentActionService.ACTION_MOVE_RIGHT
        context['ba_move_up'] = RegimentActionService.ACTION_MOVE_UP
        context['ba_move_down'] = RegimentActionService.ACTION_MOVE_DOWN

        return context


class ExecutionBattleAction(generic.TemplateView):

    def dispatch(self, request, *args, **kwargs):
        regiment = get_object_or_404(Regiment, pk=kwargs['regiment_id'])
        action = kwargs['action']

        savegame = Savegame.objects.get(pk=Savegame.objects.get_from_session(self.request))
        ras = RegimentActionService(savegame)
        ras.execute_action(regiment, action)

        return redirect('military:battle-view')


