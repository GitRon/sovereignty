from django.views import generic

from apps.location.models import Map, MapDot
from apps.location.services import MapService


class ShowMapDashboard(generic.TemplateView):
    template_name = 'show_map.html'

    def get_context_data(self, **kwargs):
        ms = MapService()

        context = super().get_context_data(**kwargs)

        context['canvas_height'] = ms.CANVAS_HEIGHT
        context['canvas_width'] = ms.CANVAS_WIDTH

        canvas_map = Map.objects.order_by('-id').first()
        if not canvas_map:
            raise Exception('Requested map is not in database.')
        if not canvas_map.is_fully_processed():
            raise Exception('Map is not fully processed.')

        context['canvas_map'] = canvas_map

        return context


class MapDotDetail(generic.TemplateView):
    template_name = 'partials/_map_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        x = self.kwargs['x'] / Map.DISPLAY_FACTOR
        y = self.kwargs['y'] / Map.DISPLAY_FACTOR
        context['map_dot'] = MapDot.objects.get(map=self.kwargs['map_id'], coordinate_x=x, coordinate_y=y)

        return context
