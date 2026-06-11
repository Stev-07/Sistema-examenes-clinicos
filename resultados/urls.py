# resultados/urls.py
from django.urls import path
from .views import *
from . import views

app_name = 'resultados'

urlpatterns = [
    path(
        'pendientes/',
        views.solicitudes_pendientes,
        name='solicitudes_pendientes'
    ),

    path(
        'completados/',
        views.resultados_completados,
        name='resultados_completados'
    ),

    path(
        'capturar/<int:examen_id>/',
        views.capturar_resultado,
        name='capturar_resultado'
    )

]