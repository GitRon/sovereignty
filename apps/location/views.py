import json

from django.contrib import messages
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.views import generic

from apps.account.managers import SavegameManager
from apps.account.models import Savegame
from apps.location.models import Map, MapDot, County
from apps.location.services.country import CountyRulerService
from apps.location.services.map import MapService


class ShowMapDashboard(generic.TemplateView):
    template_name = 'location/show_map.html'
    canvas_map = None

    def dispatch(self, request, *args, **kwargs):
        self.canvas_map = Map.objects.filter(savegame=SavegameManager.get_from_session(self.request)).first()
        if not self.canvas_map:
            messages.add_message(self.request, messages.SUCCESS, 'Current savegame does not have a map yet.')
            return redirect('account:menu-view')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ms = MapService()

        context = super().get_context_data(**kwargs)

        context['canvas_height'] = ms.CANVAS_HEIGHT
        context['canvas_width'] = ms.CANVAS_WIDTH

        if not self.canvas_map.is_fully_processed():
            raise Exception('Map is not fully processed.')

        context['county_list'] = MapDot.objects.filter(map=self.canvas_map, is_water=False) \
            .values('county__name', 'county__primary_color') \
            .annotate(province_count=Count('id')).order_by('-province_count')

        # Stats
        context['landmass'] = \
            MapDot.objects.filter(map=self.canvas_map, is_water=False).count() / \
            MapDot.objects.filter(map=self.canvas_map).count()

        context['quantity_counties'] = County.objects.filter(savegame=self.canvas_map.savegame).count()

        context['first_dot'] = MapDot.objects.filter(map=self.canvas_map, coordinate_x=0, coordinate_y=0).first()

        context['canvas_map'] = self.canvas_map

        return context


class MapDotDetail(generic.TemplateView):
    template_name = 'location/partials/_map_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        x = self.kwargs['x'] / Map.DISPLAY_FACTOR
        y = self.kwargs['y'] / Map.DISPLAY_FACTOR
        try:
            context['map_dot'] = MapDot.objects.get(map=self.kwargs['map_id'], coordinate_x=x, coordinate_y=y)
        except MapDot.DoesNotExist:
            return {}

        return context


class MyCounty(generic.DetailView):
    model = County
    template_name = 'location/my_county.html'

    def get_object(self, queryset=None):
        savegame = Savegame.objects.get(pk=SavegameManager.get_from_session(self.request))
        return savegame.playing_as.home_county

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        savegame = Savegame.objects.get(pk=SavegameManager.get_from_session(self.request))

        crs = CountyRulerService(savegame, self.object)
        context['line_of_succession'] = crs.get_succession_line()

        # todo this actually changes the amounts!
        # fys = FinishYearService(SavegameManager.get_from_session(self.request))
        #
        # Income
        # context['income'], _ = fys._gather_resources()
        #
        # # Expenses
        # context['expense_military'] = fys._military_maintenance()
        # context['expense_castle'] = fys._castle_maintenance()
        #
        # context['balance'] = context['income'] - context['expense_military'] - context['expense_castle']

        return context


class MyProvincesView(generic.DetailView):
    model = County
    template_name = 'location/my_provinces.html'

    def get_object(self, queryset=None):
        savegame = Savegame.objects.get(pk=SavegameManager.get_from_session(self.request))
        return savegame.playing_as.home_county

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['province_list'] = self.object.map_dots.all()
        return context

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ProvinceUpgradeView(generic.RedirectView):
    model = MapDot
    http_method_names = ('post',)

    def post(self, request, *args, **kwargs):
        # Gather required objects
        savegame = Savegame.objects.get(pk=SavegameManager.get_from_session(self.request))
        obj = get_object_or_404(MapDot, pk=self.kwargs.get('pk', None))

        # Do upgrade
        result = MapDot.objects.upgrade_province(province=obj, savegame=savegame)
        toast = 'Upgraded province successfully' if result else 'Upgrade not possible'

        # Build response
        response = render(request, 'location/partials/_province_detail_row.html',
                          {'province': obj, 'savegame': savegame})
        response['HX-Trigger'] = json.dumps({'refresh-my-gold': '-', 'show-toast': toast})
        return response


class MyCountyGoldView(generic.View):
    def get(self, request, *args, **kwargs):
        savegame = Savegame.objects.get(pk=SavegameManager.get_from_session(self.request))
        return HttpResponse(savegame.playing_as.home_county.gold, status=200)


class MyCountyManpowerView(generic.View):
    def get(self, request, *args, **kwargs):
        savegame = Savegame.objects.get(pk=SavegameManager.get_from_session(self.request))
        return HttpResponse(savegame.playing_as.home_county.manpower, status=200)
