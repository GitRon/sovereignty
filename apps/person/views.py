from django.views import generic

from apps.location.services.country import CreateCountyService
from apps.naming.services import LocationNameService
from apps.person.services import PersonService
from apps.person.settings import GENDER_MALE


class PersonDashboard(generic.TemplateView):
    template_name = 'person_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name'] = LocationNameService.create_name()
        context['person'] = PersonService.create_random_person(65, GENDER_MALE)
        context['county'] = CreateCountyService.create_random_county()
        return context
