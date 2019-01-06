from django.views import generic

from apps.account.managers import SavegameManager
from apps.account.models import Savegame
from apps.dynasty import settings as ps
from apps.dynasty.models import Person, Dynasty


class DynastyDashboard(generic.TemplateView):
    template_name = 'dynasty_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        savegame = Savegame.objects.get(pk=SavegameManager.get_from_session(self.request))
        context['dynasty'] = savegame.playing_as
        context['person_list'] = Person.objects.get_visible(self.request).filter(
            dynasty=context['dynasty']).order_by('birth_year')
        context['gender_male'] = ps.GENDER_MALE
        return context


class PersonDetail(generic.DetailView):
    model = Person
    template_name = 'person_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['gender_male'] = ps.GENDER_MALE
        return context
