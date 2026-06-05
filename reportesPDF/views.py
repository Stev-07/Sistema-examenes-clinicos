from django.shortcuts import render
# Create your views here.
import io
from django.http import HttpResponse
from django.utils.timezone import now
# Componentes de ReportLab
from reportlab.lib.pagesizes import letter
from reportlab.platypus import PageBreak, SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from examenes.models import Orden, ExamenRealizado, TipoExamen
from .models import ConfiguracionReporte
from django.shortcuts import get_object_or_404
from reportlab.platypus import SimpleDocTemplate
from .services.diseño_categoria import *
from .services.datos_fijos import *


def generar_reporte_completo_pdf(request, orden_id):
    orden = get_object_or_404(Orden, id=orden_id)
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    # Datos fijos para el diccionario del encabezado de la clínica
    datos_clinica = {
        'nombre': 'Sucursal 3',
        'ubicacion': 'Condominio Clínicas Médicas, Primer Nivel, Local 16, Sobre 25 Av. Norte.',
        'departamento': 'San Salvador',
        'numero_telefono': '2562-2057'
    }
    
    # 1. Obtener todos los exámenes de la orden ordenados por su Perfil Médico
    examenes_realizados = ExamenRealizado.objects.filter(orden=orden).select_related('tipo_examen').order_by('tipo_examen__perfil')
    
    perfil_actual = None
    es_primera_pagina = True
    
    # 2. Iterar sobre cada examen realizado
    for examen in examenes_realizados:
        perfil_del_examen = examen.tipo_examen.perfil
        
        # LOGICA DE SALTO DE PÁGINA: Si cambia el perfil, forzamos nueva hoja
        if perfil_actual is not None and perfil_actual != perfil_del_examen:
            story.append(PageBreak())
            es_primera_pagina = True # Marcamos que iniciamos nueva hoja institucional
            
        # Si es el inicio de una página (la primera o una nueva por cambio de perfil)
        if es_primera_pagina:
            story.append(generar_encabezado_clinica(datos_clinica))
            story.append(Spacer(1, 15))
            story.append(generar_bloque_paciente(orden))
            story.append(Spacer(1, 20))
            es_primera_pagina = False
            perfil_actual = perfil_del_examen
            
        # 3. DETECTAR EL TIPO DE DISEÑO (Consultando el modelo ConfiguracionReporte)
        config = ConfiguracionReporte.objects.filter(tipo_examen=examen.tipo_examen).first()
        tipo_diseno = config.tipo if config else 'TABLA' # Por defecto usa TABLA si no está configurado
        
        # 4. Inyectar el diseño correspondiente al flujo
        if tipo_diseno == 'TABLA':
            story.append(generar_diseno_tabla(examen))
        elif tipo_diseno == 'CATEGORIZADO':
            story.append(generar_diseno_categorizado(examen))
        elif tipo_diseno == 'IMAGEN':
            story.append(generar_diseno_imagen(examen))
            
        # Espacio de separación entre exámenes del mismo perfil
        story.append(Spacer(1, 20))
        
    # 5. Construcción final del documento
    doc.build(story)
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Reporte_Orden_{orden.correlativo}.pdf"'
    return response