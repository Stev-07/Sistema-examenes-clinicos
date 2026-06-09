from urllib import request
from django.contrib import messages
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from clientes.models import Cliente, Expediente
from clientes.services import calcular_edad

styles = getSampleStyleSheet()
style_normal = styles['Normal']

def get_name_patient(orden):
    try:
        expediente = Expediente.objects.get(numero_expediente=orden.expediente.numero_expediente)
        cliente = expediente.cliente.usuario.first_name + " " + expediente.cliente.usuario.last_name
        return cliente.upper()
    except Expediente.DoesNotExist:
        print(f"El expediente con número {orden.expediente.numero_expediente} no existe.")
        messages.error(request, f"Error: NO EXISTE")
        return "NOMBRE NO DISPONIBLE"

def get_edad_patient(orden):
    try:
        expediente = Expediente.objects.get(numero_expediente=orden.expediente.numero_expediente)
        cliente = expediente.cliente
        edad = calcular_edad(cliente.fecha_nacimiento)
        return f"{edad} Años"
    except Expediente.DoesNotExist:
        print(f"El expediente con número {orden.expediente.numero_expediente} no existe.")
        messages.error(request, f"Error: NO EXISTE")
        return "EDAD NO DISPONIBLE"

def get_genero(orden):
    try:
        expediente = Expediente.objects.get(numero_expediente=orden.expediente.numero_expediente)
        cliente = expediente.cliente
        return cliente.sexo
    except Expediente.DoesNotExist:
        print(f"El expediente con número {orden.expediente.numero_expediente} no existe.")
        messages.error(request, f"Error: NO EXISTE")
        return "GÉNERO NO DISPONIBLE"
# --- ENCABEZADO ---
#recibe lo datos de la clinica y genera el encabezado
def generar_encabezado_clinica(datos_clinica):
    style_titulo = ParagraphStyle(
        'TituloLab', parent=styles['Heading1'], fontSize=22, leading=26,
        textColor=colors.HexColor('#0000BB'), fontName='Helvetica-Bold'
    )
    style_derecha = ParagraphStyle('Der', parent=style_normal, alignment=2)
    
    data = [[
        Paragraph("<b>FIAMEDS</b><br/><font size=10 color='#555'>Laboratorios Clínicos</font>", style_titulo),
        Paragraph(f"<b>{datos_clinica['nombre']}</b><br/>{datos_clinica['ubicacion']}<br/>{datos_clinica['departamento']} | Tel: {datos_clinica['numero_telefono']}", style_derecha)
    ]]
    
    tabla = Table(data, colWidths=[250, 282])
    tabla.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    return tabla

# --- DATOS DEL PACIENTE ---
def generar_bloque_paciente(orden):
    nombre_medico = orden.doctor if orden.doctor else "No especificado"
    
    # Intentamos obtener la fecha de la orden si existe en tu modelo, si no, dejamos "N/A"
    fecha_orden = orden.fechaEmision.strftime('%d/%m/%Y') if hasattr(orden, 'fechaEmision') and orden.fechaEmision else "N/A"

    data = [
        ["Nombre del paciente", "Edad"],
        [get_name_patient(orden), get_edad_patient(orden)],
        ["No. Expediente", "Género"],
        [orden.expediente.numero_expediente, get_genero(orden)],
        ["Médico Recetante", "Fecha de Orden"], 
        [nombre_medico, fecha_orden]         
    ]   
    
    tabla = Table(data, colWidths=[400, 132])
    tabla.setStyle(TableStyle([
        # Fila 0 (Títulos superiores)
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F0F4F8')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        
        # Fila 2 (Títulos del medio)
        ('BACKGROUND', (0,2), (-1,2), colors.HexColor('#F0F4F8')),
        ('FONTNAME', (0,2), (-1,2), 'Helvetica-Bold'),
        
        # Fila 4 (Nuevos títulos inferiores: Médico y Fecha)
        ('BACKGROUND', (0,4), (-1,4), colors.HexColor('#F0F4F8')),
        ('FONTNAME', (0,4), (-1,4), 'Helvetica-Bold'),
        
        # Estilos generales para toda la tabla
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#0000BB')),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    return tabla

# --- RESULTADOS DE UN EXAMEN (Reutilizable para múltiples exámenes) ---
def generar_tabla_examen(nombre_examen, resultados_queryset):
    style_centro = ParagraphStyle('Cen', parent=style_normal, alignment=1)
    
    # Encabezado con el nombre del Examen/Categoría (ej: QUIMICA CLINICA)
    filas = [
        [Paragraph(f"<b>EXAMEN: {nombre_examen.upper()}</b>", style_normal), "", "", ""],
        ["Prueba", "Resultado", "Unidades", "Rangos de Referencia"]
    ]
    
    # Mapeo de los resultados de este examen en particular
    for item in resultados_queryset:
        celda_prueba = Paragraph(f"<b>{item.nombre_prueba}</b>", style_normal)
        celda_resultado = Paragraph(f"<b>{item.resultado}</b>", style_centro)
        celda_rangos = Paragraph(item.rango_referencia.replace("\n", "<br/>"), style_normal)
        
        filas.append([celda_prueba, celda_resultado, item.unidades, celda_rangos])
        
    tabla = Table(filas, colWidths=[182, 100, 80, 170])
    tabla.setStyle(TableStyle([
        # Unir celdas de la primera fila para el título del examen
        ('SPAN', (0,0), (3,0)),
        ('BACKGROUND', (0,0), (3,0), colors.HexColor('#1A365D')),
        ('TEXTCOLOR', (0,0), (3,0), colors.white),
        # Estilo para la cabecera de las columnas
        ('LINEBELOW', (0,1), (-1,1), 1.5, colors.HexColor('#0000BB')),
        ('FONTNAME', (0,1), (-1,1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0,1), (-1,1), colors.HexColor('#1A365D')),
        # Estilos generales de las celdas
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    return tabla