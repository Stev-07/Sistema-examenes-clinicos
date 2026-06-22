from django import forms
from .models import Orden, Doctor
from django.core.validators import RegexValidator
from datetime import date
from django.core.validators import MaxValueValidator, MinValueValidator

solo_letras = RegexValidator(
    regex=r'^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$',
    message='Solo se permiten letras.'
)

class DoctorForm(forms.Form):
    nombreD = forms.CharField(
        max_length=100,
        validators=[solo_letras],
        label='Nombre del doctor',
        widget=forms.TextInput(attrs={'id': 'nombre-doctor', 'placeholder': 'Nombre del doctor'})
    )
    jvpm = forms.IntegerField(
        label='JVPM',
        widget=forms.NumberInput(attrs={'id': 'jvpm', 'placeholder': 'JVPM del doctor'})
    )

    def clean_jvpm(self):
        jvpm = str(self.cleaned_data['jvpm'])

        if len(jvpm) != 8:
            raise forms.ValidationError(
                'El JVPM debe tener exactamente 8 dígitos.'
            )

        return int(jvpm)

class OrdenForm(forms.Form):
    correlativo = forms.IntegerField(
        label='Correlativo',
        validators=[

            MinValueValidator(1),
            MaxValueValidator(999999999) #máximo 10 digitos
        ],
        widget=forms.NumberInput(attrs={'placeholder': 'Número correlativo',
        'max': '9999999999',
        'oninput': 'this.value = this.value.slice(0, 9)'})
    )
    fechaEmision = forms.DateField(
        label='Fecha de emisión',
        widget=forms.DateInput(attrs={'type': 'date', 'max': date.today().isoformat()})
    )
    total = forms.DecimalField(max_digits=8, decimal_places=2, widget=forms.HiddenInput())
    examenes = forms.CharField(widget=forms.HiddenInput(), required=False)

    def clean_fechaEmision(self):
        fecha = self.cleaned_data['fechaEmision']

        if fecha > date.today():
            raise forms.ValidationError(
                'No puede seleccionar una fecha futura.'
            )

        return fecha