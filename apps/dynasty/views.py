from django.views import generic

from apps.account.models import Savegame
from apps.dynasty import settings as ps
from apps.dynasty.models import Person
from apps.dynasty.services import PersonService


class DynastyDashboard(generic.TemplateView):
    template_name = 'dynasty_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ruler'] = Person.objects.all().last()
        return context

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     person_service = PersonService()
    #     savegame = Savegame.objects.get_from_session(self.request)
    #     context['ruler'] = person_service.create_random_person(savegame, 65, ps.GENDER_MALE)
    #     return context


class PersonDetail(generic.DetailView):
    model = Person
    template_name = 'person_detail.html'
