from django import forms

from .models import Event

class EventAdminForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()

        enable_registration = cleaned_data.get('enable_registration')
        registration_url = cleaned_data.get('registration_url')
        enable_tickets = cleaned_data.get('enable_tickets')
        ticket_url = cleaned_data.get('ticket_url')

        errors = {}

        if enable_registration and not registration_url:
            errors['registration_url'] = 'Укажите ссылку на регистрацию, если она включена.'

        if enable_tickets and not ticket_url:
            errors['ticket_url'] = 'Укажите ссылку на покупку билетов, если она включена.'

        if errors:
            raise forms.ValidationError(errors)

        return cleaned_data