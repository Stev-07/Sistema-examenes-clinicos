from urllib import request
from django.contrib import messages
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


styles = getSampleStyleSheet()
style_normal = styles['Normal']
def get_tipo_muestra(examen_realizado):

    if hasattr(examen_realizado.tipo_examen, 'muestra'):
        return examen_realizado.tipo_examen.muestra.upper()
    return "MUESTRA DESCONOCIDA"


# --- DISEÑO : REPORTE TIPO TABLA 
def generar_diseno_tabla(examen_realizado):
    style_centro = ParagraphStyle('Cen', parent=style_normal, alignment=1)
    
    # Cabecera de la sección con el nombre del examen
    filas = [
        [Paragraph(f"<b>MUESTRA: {get_tipo_muestra(examen_realizado)} / {examen_realizado.tipo_examen.nombre.upper()}</b>", style_normal), "", "", ""],
        ["Prueba", "Resultado", "Unidades", "Rangos de Referencia"]
    ]
    
    # Obtener los parámetros/resultados de este examen realizado
    resultados = examen_realizado.resultados.all().select_related('parametro')
    for r in resultados:
        celda_prueba = Paragraph(f"<b>{r.parametro.nombreP}</b>", style_normal)
        celda_resultado = Paragraph(f"<b>{r.valor}</b>", style_centro)
        celda_unidades = r.parametro.unidadMedida
        celda_rangos = Paragraph(r.parametro.valorNorma.replace("\n", "<br/>"), style_normal)
        
        filas.append([celda_prueba, celda_resultado, celda_unidades, celda_rangos])
        
    tabla = Table(filas, colWidths=[182, 100, 80, 170])
    tabla.setStyle(TableStyle([
        ('SPAN', (0,0), (3,0)),
        ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor('#0000BB')),
        ('LINEBELOW', (0,1), (-1,1), 1.5, colors.HexColor('#0000BB')),
        ('FONTNAME', (0,1), (-1,1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,1), (-1,1), colors.HexColor('#1A365D')),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    return tabla


# --- DISEÑO : REPORTE CATEGORIZADO (Estructura en bloques/párrafos)
def generar_diseno_categorizado(examen_realizado):
    filas = [
        [Paragraph(f"<b>ANÁLISIS DETALLADO: {examen_realizado.tipo_examen.nombre.upper()}</b>", style_normal), ""]
    ]
    
    resultados = examen_realizado.resultados.all().select_related('parametro')
    for r in resultados:
        # Formato limpio de dos columnas anchas: Componente a la izquierda, descripción detallada a la derecha
        celda_componente = Paragraph(f"<b>• {r.parametro.nombreP}:</b>", style_normal)
        celda_descripcion = Paragraph(f"{r.valor} <font color='#555'>({r.parametro.unidadMedida})</font>", style_normal)
        filas.append([celda_componente, celda_descripcion])
        
    tabla = Table(filas, colWidths=[180, 352])
    tabla.setStyle(TableStyle([
        ('SPAN', (0,0), (1,0)),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F0F4F8')),
        ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor('#0000BB')),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    return tabla


# --- DISEÑO : REPORTE TIPO IMAGEN (Contenedor estructurado para gráficos o adjuntos) 
def generar_diseno_imagen(examen_realizado):
    # Crea un recuadro limpio y estandarizado que sirva como marcador de posición o contenedor visual
    filas = [
        [Paragraph(f"<b>REGISTRO GRÁFICO / IMAGEN: {examen_realizado.tipo_examen.nombre.upper()}</b>", style_normal)],
        [Spacer(1, 10)],
        [Paragraph("<font color='#555'>[ Espacio Estructurado para Gráfico o Imagen Adjunta de Diagnóstico ]</font>", style_normal)],
        [Spacer(1, 10)],
        [Paragraph(f"<b>Observaciones del Analista:</b> {examen_realizado.observaciones or 'Ninguna'}", style_normal)]
    ]
    
    tabla = Table(filas, colWidths=[532])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F0F4F8')),
        ('ALIGN', (0,2), (-1,2), 'CENTER'),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#0000BB')), # Recuadro exterior limpio
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    return tabla