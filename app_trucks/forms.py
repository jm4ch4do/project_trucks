from django.forms import ModelForm
from app_trucks.models import *
from django.forms import Field
from django import forms
from django.core.exceptions import ValidationError


# Overwrite error messages.
Field.default_error_messages = {
    'required': "Este valor es obligatorio",
    'invalid': "Este valor no está permitido",
    'invalid_choice': u'Value %r is not a valid choice',
    'null': u'This field cannot be null.',
    'blank': u'This field cannot be blank.',
}


class WorkDayForm(ModelForm):
    class Meta:
        model = WorkDay

        readonly_fields = ('date_created',)

        fields = [
            'date',
            'truck',

            'ini_mileage',
            'end_mileage',

            'income',

            'comment',
        ]

        error_messages = {
            'ini_mileage': {
                'invalid': "Introduzca un valor numérico",
            },
            'end_mileage': {
                'invalid': 'Introduzca un valor numérico',
            },
        }


class DeliveryForm(ModelForm):
    # temp_company_name = forms.CharField()

    class Meta:
        model = Delivery
        exclude = ()


class DateForm(forms.Form):
    date = forms.DateField()


class ReportForm(forms.Form):

    #
    # ----------------------- FIELDS ---------------------------------------------------------------

    # --------- Truck Select ---------
    truck_choices = Truck.get_trucks_as_choices()
    truck = forms.ChoiceField(choices=truck_choices)

    # --------- User Select ---------
    user_choices = Worker.get_workers_as_choices()
    user = forms.ChoiceField(choices=user_choices)

    # --------- Date Pick ---------
    date_ini = forms.DateField(required=False)
    date_end = forms.DateField(required=False)

    #
    # --------------------- VALIDATION -------------------------------------------------------------
    def clean_truck(self):
        data = self.cleaned_data['truck']
        truck_choices = Truck.get_trucks_as_choices()
        truck_ids = [truck_choice[0] for truck_choice in truck_choices]
        if int(data) not in truck_ids:
            raise ValidationError(
                'El valor proprocionado no es apropiado',
                code='bad_choice',
            )

        return int(data)

    def clean_user(self):
        data = self.cleaned_data['user']
        user_choices = Worker.get_workers_as_choices()
        user_ids = [user_choice[0] for user_choice in user_choices]
        if int(data) not in user_ids:
            raise ValidationError(
                'El valor proporcionado no es apropiado',
                code='bad_choice',
            )

        return int(data)
