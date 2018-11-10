from django.views import generic

from apps.naming.services import PersonNameService


class PersonDashboard(generic.TemplateView):
    template_name = 'person_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['name'] = PersonNameService.create_name()
        return context
