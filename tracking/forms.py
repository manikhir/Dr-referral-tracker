from django import forms
import autocomplete_light
from tracking.models import *


class OrganizationForm(forms.ModelForm):
    """
    Create a new organization,
    Check for duplicates
    Offer new NewAgent creation in same form.
    """

    class Meta:
        model = Organization
        exclude = []


class AgentForm(autocomplete_light.ModelForm):
    """
    Create a new Agent
    autocomplete Organization https://github.com/yourlabs/django-autocomplete-light/tree/stable/2.x.x
    Check for duplicates
    Offer new NewAgent creation
    """

    class Meta:
        model = Agent
        exclude = []


class PatientVisitForm(autocomplete_light.ModelForm):
    """
    record a new patient visit
    autocomplete Agent
    Don't need blank for Org
    Assume today's date
    """

    class Meta:
        model = PatientVisit
        exclude = ['patient_visit_date']


class PatientVisitHistoryForm(forms.Form):
    """
    record a new patient_visit
    autocomplete Agent
    Don't need blank for Org
    Assume today's date
    """

    agent = autocomplete_light.ModelMultipleChoiceField('AgentAutocomplete', required=False)
    from_date = forms.DateField(widget=forms.TextInput(attrs={'readonly' : 'readonly'}))
    to_date = forms.DateField(widget=forms.TextInput(attrs={'readonly' : 'readonly'}))
