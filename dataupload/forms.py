from django import forms
from django.core.exceptions import ValidationError


class UploadFileForm(forms.Form):
    tipo = forms.ChoiceField(choices=(('dati', 'Dati climatici'), ('stazioni', 'Database stazioni meteo')))
    file = forms.FileField(allow_empty_file=False)