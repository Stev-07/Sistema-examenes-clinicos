from django.shortcuts import render
from .services import *

# Create your views here.
def create_expediente(request):
    try:
        resultado = create_expediente_service(request)
        print(resultado)
    except Exception as e:
        print(f"Error al crear expediente: {e}")
    return render(request, 'create_expediente.html')
