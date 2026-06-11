from django import forms

class ResultadoForm(forms.Form):
    
    def __init__(self, parametros, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for parametro in parametros:
            if parametro.tipo == 'cuant':
                self.fields[f'resultado_{parametro.id}'] = forms.FloatField(
                    label=parametro.nombreP,
                    required=True,
                    widget=forms.NumberInput(attrs={
                        'placeholder': 'Ingrese valor numérico',
                        'step': '0.01'
                    })
                )
            elif parametro.tipo == 'porc':
                self.fields[f'resultado_{parametro.id}'] = forms.FloatField(
                    label=parametro.nombreP,
                    min_value=0,
                    max_value=100,
                    required=True,
                    widget=forms.NumberInput(attrs={
                        'placeholder': '0 - 100',
                        'step': '0.01',
                        'min': '0',
                        'max': '100'
                    })
                )
            elif parametro.tipo == 'cuali':
                self.fields[f'resultado_{parametro.id}'] = forms.ChoiceField(
                    label=parametro.nombreP,
                    choices=[
                        ('', 'Seleccionar'),
                        ('Positivo', 'Positivo'),
                        ('Negativo', 'Negativo'),
                        ('Reactivo', 'Reactivo'),
                        ('No Reactivo', 'No Reactivo'),
                        ('Detectado', 'Detectado'),
                        ('No Detectado', 'No Detectado'),
                        ('Presente', 'Presente'),
                        ('Ausente', 'Ausente'),
                        ('Normal', 'Normal'),
                        ('Anormal', 'Anormal'),
                    ],
                    required=True
                )
            else:
                self.fields[f'resultado_{parametro.id}'] = forms.CharField(
                    label=parametro.nombreP,
                    required=True,
                    widget=forms.TextInput(attrs={
                        'placeholder': 'Ingrese resultado'
                    })
                )