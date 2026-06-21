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
from reportesPDF.models import ResultadosExamenesPDF
from .models import ConfiguracionReporte
from django.shortcuts import get_object_or_404
from reportlab.platypus import SimpleDocTemplate
from .services.diseño_categoria import *
from .services.datos_fijos import *
from usuarios.services.validacion_grupo import grupos_requeridos

"""Funcion auxiliar para obtener los datos de la clinica que emite los resultados"""
def get_datos_clinica(request, orden):
    if request.user.groups.filter(name='Laboratoristas').exists():
        return request.user.sucursal.to_dict()
    if request.user.groups.filter(name='Recepcionistas').exists():
        return request.user.sucursal.to_dict()
    if request.user.groups.filter(name='Pacientes').exists():
        datos = ResultadosExamenesPDF.objects.get(correlativo = orden.id)
        clinica = datos.AnalistaClinico.usuario.sucursal.to_dict()
        return clinica

#Función para generar el buffer
def generar_reporte_completo_pdf(request,orden):
    buffer = io.BytesIO()
    
    #el topMargin a 180
    # para que los exámenes empiecen a dibujarse ABAJO del encabezado fijo.
    doc = SimpleDocTemplate(
        buffer, pagesize=letter, 
        rightMargin=40, leftMargin=40, 
        topMargin=210, bottomMargin=40
    )
    story = []
    
    datos_clinica = get_datos_clinica(request, orden)
    
    # Obtener y agrupar exámenes por perfil
    examenes_realizados = ExamenRealizado.objects.filter(orden=orden, estado='completado').select_related('tipo_examen').order_by('tipo_examen__perfil')
    
    examenes_por_perfil = {}
    for examen in examenes_realizados:
        perfil = examen.tipo_examen.perfil
        if perfil not in examenes_por_perfil:
            examenes_por_perfil[perfil] = []
        examenes_por_perfil[perfil].append(examen)
    
    # Armar el flujo (story) de exámenes
    for indice, (perfil, examenes) in enumerate(examenes_por_perfil.items()):
        if indice > 0:
            story.append(PageBreak()) # Salto de página entre perfiles diferentes
        
        for examen in examenes:
            config = ConfiguracionReporte.objects.filter(tipo_examen=examen.tipo_examen).first()
            tipo_diseno = config.tipo if config else 'TABLA'
            
            if tipo_diseno == 'TABLA':
                story.append(generar_diseno_tabla(examen))
            elif tipo_diseno == 'CATEGORIZADO':
                story.append(generar_diseno_categorizado(examen))
            elif tipo_diseno == 'IMAGEN':
                story.append(generar_diseno_imagen(examen))
                
            story.append(Spacer(1, 20))
            
    #funcion que agrega encabezado en cada página
    def encorporar_decoracion(canvas, documento):
        encabezado = generar_encabezado_clinica(datos_clinica)
        bloque_paciente = generar_bloque_paciente(orden)

        encabezado.wrapOn(canvas, doc.width, doc.topMargin)
        bloque_paciente.wrapOn(canvas, doc.width, doc.topMargin)

        # El membrete se queda arriba fijado en 700
        encabezado.drawOn(canvas, doc.leftMargin, 700)
        bloque_paciente.drawOn(canvas, doc.leftMargin, 590)

        #footer legal
        # El origen (0,0) es la esquina inferior izquierda.
        x_cuadrado = doc.leftMargin              # Alineado con el margen izquierdo (40)
        y_cuadrado = 35                          # Distancia desde el borde inferior de la hoja
        ancho_cuadrado = doc.width               # Mismo ancho que el contenido (Letter width - márgenes)
        alto_cuadrado = 45                       # Altura de la caja para que quepan las dos líneas
        
        # Configurar el estilo del cuadrado
        canvas.setStrokeColorRGB(0.7, 0.7, 0.7)  
        canvas.setLineWidth(1)                   # Grosor de la línea
        
        # Dibujar el rectángulo: rect(x, y, ancho, alto)
        canvas.rect(x_cuadrado, y_cuadrado, ancho_cuadrado, alto_cuadrado, stroke=1, fill=0)
        
        # Configurar la tipografía para el texto 
        canvas.setFont("Helvetica-Bold", 8)      # Fuente en negrita y tamaño pequeño
        canvas.setFillColorRGB(0.2, 0.2, 0.2)    # Color de texto gris oscuro/negro
        
        # Escribir las líneas de texto dentro del cuadrado
        # Ajustamos las coordenadas Y para que queden centradas verticalmente dentro de la caja
        linea1 = "1 - Los resultados de análisis clínicos deben ser interpretados por un médico."
        linea2 = "2 - Es responsabilidad del paciente el manejo de resultados no ordenados por un médico."
        
        # drawString(x, y, texto) -> sumamos +10 a la X para dejar un margen izquierdo interno
        canvas.drawString(x_cuadrado + 10, y_cuadrado + 26, linea1) 
        canvas.drawString(x_cuadrado + 10, y_cuadrado + 12, linea2)

    # reportlab añadira encabezado y footer a cada pagina usando esta def 
    doc.build(story, onFirstPage=encorporar_decoracion, onLaterPages=encorporar_decoracion)
    
    buffer.seek(0)
    #response = HttpResponse(buffer, content_type='application/pdf')
    #response['Content-Disposition'] = f'inline; filename="Reporte_Orden_{orden.correlativo}.pdf"'
    return buffer

#Función para generar el PDF
@grupos_requeridos('Laboratoristas', 'Recepcionistas', 'Pacientes')
def generar_pdf(request, orden_id):
    """Vista que usa generar_pdf_buffer y retorna la respuesta HTTP"""
    orden = get_object_or_404(Orden, id=orden_id)
    buffer = generar_reporte_completo_pdf(request, orden)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Reporte_Orden_{orden.correlativo}.pdf"'
    return response