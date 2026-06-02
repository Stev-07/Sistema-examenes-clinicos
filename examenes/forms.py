from django import forms
from .models import Orden, Doctor

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
    expediente_id = forms.IntegerField(widget=forms.HiddenInput(attrs={'id': 'expediente-id-hidden'}))
    correlativo = forms.IntegerField(widget=forms.HiddenInput(attrs={'id': 'correlativo-hidden'}))
    total = forms.DecimalField(max_digits=8, decimal_places=2, widget=forms.HiddenInput())
    examenes = forms.CharField(widget=forms.HiddenInput())