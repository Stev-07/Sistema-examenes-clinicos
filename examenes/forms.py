from django import forms
from .models import Orden, Doctor
from django.core.validators import MaxValueValidator, MinValueValidator

class DoctorForm(forms.Form):
    nombreD = forms.CharField(
        max_length=100,
        label='Nombre del doctor',
        widget=forms.TextInput(attrs={'id': 'nombre-doctor', 'placeholder': 'Nombre del doctor'})
    )
    jvpm = forms.IntegerField(
        label='JVPM',
        widget=forms.NumberInput(attrs={'id': 'jvpm', 'placeholder': 'JVPM del doctor'})
    )

class OrdenForm(forms.Form):
    correlativo = forms.IntegerField(
        label='Correlativo',
        validators=[

            MinValueValidator(1),
            MaxValueValidator(9999999999) #máximo 10 digitos
        ],
        widget=forms.NumberInput(attrs={'placeholder': 'Número correlativo',
        'max': '9999999999',
        'oninput': 'this.value = this.value.slice(0, 10)'})
    )
    fechaEmision = forms.DateField(
        label='Fecha de emisión',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    total = forms.DecimalField(max_digits=8, decimal_places=2, widget=forms.HiddenInput())
    examenes = forms.CharField(widget=forms.HiddenInput(), required=False)