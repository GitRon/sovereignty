from django.contrib import messages
from django.urls import reverse
from django.views import generic

from apps.account.managers import SavegameManager
from apps.account.models import Savegame
from apps.dynasty import settings as ps
from apps.dynasty.forms import MarryForm
from apps.dynasty.models import Person
from apps.dynasty.services import MarriageService


class DynastyOverviewView(generic.TemplateView):
    template_name = 'dynasty_overview.html'

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
        context['title_claims'] = self.object.get_title_claims()
        return context


class MarriageView(generic.TemplateView):
    template_name = 'marriage_overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        savegame_id = Savegame.objects.get_from_session(self.request)
        ms = MarriageService(savegame_id)

        context['marriageable_women'] = ms.get_marriageable_persons(ps.GENDER_FEMALE)
        context['marriageable_men'] = ms.get_marriageable_persons(ps.GENDER_MALE)

        context['count_own_marriageable_women'] = ms.get_marriageable_person_of_own_dynasty(ps.GENDER_FEMALE).count()
        context['count_own_marriageable_men'] = ms.get_marriageable_person_of_own_dynasty(ps.GENDER_MALE).count()

        return context


class MarryingFormView(generic.FormView):
    form_class = MarryForm
    template_name = 'marriage_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['savegame_id'] = Savegame.objects.get_from_session(self.request)
        kwargs['other_person'] = self.kwargs['other_person']
        return kwargs

    def form_valid(self, form):

        form.cleaned_data['my_person'].spouse = form.cleaned_data['other_person']
        form.cleaned_data['my_person'].save()
        form.cleaned_data['other_person'].spouse = form.cleaned_data['my_person']
        form.cleaned_data['other_person'].save()

        messages.add_message(self.request, messages.SUCCESS, 'Marriage was successfully sealed.')

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dynasty:marriage-view')
