from django.urls import path
from .views import *

app_name = 'reportesPDF'

urlpatterns = [
    path('generate/<int:orden_id>/', generar_reporte_completo_pdf, name='generate_report_pdf'),
    
]