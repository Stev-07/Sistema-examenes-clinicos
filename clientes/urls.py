from django.urls import path
from . import views
from django.http import HttpResponse

app_name = 'pacientes'

urlpatterns = [
    path('prueba/', lambda request: HttpResponse("FUNCIONA")),
    path('create_exp/', views.create_paciente_expediente, name='crea_expediente'),
    path('dashboard/', views.dashboard_paciente, name='dashboard_paciente'),
    path('examen/<int:examen_id>/ver/', views.ver_pdf_examen, name='ver_pdf_examen'),
    path('examen/<int:examen_id>/descargar/', views.descargar_pdf_examen, name='descargar_pdf_examen'),
    path('buscar/', views.buscar_cliente_existente, name='buscar_cliente_existente'),
]
