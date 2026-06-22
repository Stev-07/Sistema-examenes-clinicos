from django import forms
from .models import Cliente
from datetime import date
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
Usuario = get_user_model()

class UsuarioDatosForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}),
        }
        labels = {
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
        }

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['n_dui', 'fecha_nacimiento', 'correo_electronico', 'sexo']
        widgets = {
            'n_dui': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresar el número de DUI sin guiones'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date', 'max': date.today().isoformat()
            }),
            'correo_electronico': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingresar el correo electrónico del paciente'
            }),
            'sexo': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

        labels = {
            'correo_electronico': 'Correo Electrónico',
            'n_dui': 'N° de DUI',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'sexo': 'Sexo',
        }
