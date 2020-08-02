from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Submit
from django import forms
from django.core.exceptions import ValidationError

from apps.dynasty.models import Person
from apps.dynasty.services import MarriageService
from apps.dynasty.utils import get_opposite_gender


class MarryForm(forms.Form):
    my_person = forms.ModelChoiceField(queryset=Person.objects.all(), empty_label=None)
    other_person = forms.ModelChoiceField(queryset=Person.objects.all(), empty_label=None)

    def __init__(self, *args, **kwargs):
        self.ms = MarriageService(kwargs.pop('savegame_id'))

        other_person_id = kwargs.pop('other_person')
        other_person = Person.objects.get(pk=other_person_id)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Div(
                Div('my_person'),
                Div('other_person'),
                css_class='input-field col s12'),
            Div(
                Submit('submit', 'Yes, I do!', css_class="btn"),
                css_class='input-field col s12'),

        )

        super().__init__(*args, **kwargs)

        self.fields['my_person'].queryset = self.ms.get_marriageable_person_of_own_dynasty(
            get_opposite_gender(other_person.gender))
        self.fields['other_person'].queryset = Person.objects.filter(pk=other_person_id)
        self.fields['other_person'].initial = other_person


def clean_my_person(self):
    data = self.cleaned_data['my_person']

    if data not in self.ms.get_marriageable_person_of_own_dynasty(data.gender):
        raise ValidationError('My person cannot marry!')

    return data


def clean_other_person(self):
    data = self.cleaned_data['other_person']

    if data not in self.ms.get_marriageable_persons(data.gender):
        raise ValidationError('Other person cannot marry!')

    return data
