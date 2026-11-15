from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .models import Etiqueta, Usuario


class RegistroForm(forms.Form):
    username = forms.CharField(
        max_length=50,
        label='Nombre de usuario',
        validators=get_user_model()._meta.get_field('username').validators,
        widget=forms.TextInput(attrs={'autocomplete': 'username'}),
    )
    password1 = forms.CharField(
        min_length=8,
        label='Contraseña',
        help_text='Mínimo 8 caracteres',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    password2 = forms.CharField(
        min_length=8,
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        user_model = get_user_model()
        if user_model._default_manager.filter(username=username).exists():
            raise ValidationError('Ya existe una cuenta con ese nombre de usuario.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Las contraseñas no coinciden.')
        return cleaned_data

    def save(self):
        user_model = get_user_model()
        return user_model._default_manager.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password1'],
        )


class PreferenciasForm(forms.ModelForm):
    ubicacion_confirmada = forms.BooleanField(
        required=True,
        widget=forms.HiddenInput,
        error_messages={'required': 'Busca una dirección, usa tu ubicación o selecciónala en el mapa.'},
    )
    gustos = forms.ModelMultipleChoiceField(
        queryset=Etiqueta.objects.filter(activo=True).order_by('nombre'),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label='Gustos',
        help_text='Selecciona al menos dos gustos.',
    )
    latitud = forms.FloatField(
        min_value=-90,
        max_value=90,
        widget=forms.HiddenInput,
    )
    longitud = forms.FloatField(
        min_value=-180,
        max_value=180,
        widget=forms.HiddenInput,
    )
    distancia_maxima = forms.IntegerField(
        min_value=1,
        label='Distancia máxima a la que estas dispuesto a viajar (km)',
        help_text='Ingresa una distancia de al menos 1 km.',
        error_messages={
            'required': 'Indica la distancia máxima.',
            'invalid': 'Ingresa un número entero válido.',
            'min_value': 'El valor debe ser mayor o igual que 1.',
        },
    )

    class Meta:
        model = Usuario
        fields = ('gustos', 'latitud', 'longitud', 'distancia_maxima')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and not self.is_bound:
            self.initial['ubicacion_confirmada'] = True

    def clean_gustos(self):
        gustos = self.cleaned_data['gustos']
        if gustos.count() < 2:
            raise ValidationError('Selecciona al menos dos gustos.')
        return gustos
