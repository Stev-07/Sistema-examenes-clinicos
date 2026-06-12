from django.shortcuts import render,redirect
from django.contrib import messages
from .forms import *
from .services import *
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from examenes.models import ExamenRealizado 

# Create your views here.
def create_paciente_expediente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        form_user = UsuarioDatosForm(request.POST)
        if form.is_valid() and form_user.is_valid():
            Nuevopaciente = create_expediente_service(form, form_user)

            #variables de sesion para mostrar mensaje de éxito
            request.session['expediente_numero'] = Nuevopaciente['expediente'].numero_expediente
            messages.success(request, f"Se ha creado con éxito el expediente para {Nuevopaciente['usuario'].first_name} {Nuevopaciente['usuario'].last_name} con número de expediente {Nuevopaciente['expediente'].numero_expediente}.")
            if request.user.groups.filter(name='Recepcionistas').exists():
                return redirect('usuarios:recepcionista_dashboard')
            return redirect('usuarios:login')

        print("Errores del formulario:", form.errors)  # Debug: Verificar errores del formulario
        print("Errores del formulario de usuario:", form_user.errors)  # Debug: Verificar errores del formulario de usuario
        messages.error(request, "Error al crear el expediente. Por favor, revise los datos ingresados.")
        return render(request, 'create_paciente.html', {'form': form, 'form_user': form_user})
            
    else:
        form = ClienteForm()
        form_user = UsuarioDatosForm()
        return render(request, 'create_paciente.html', {'form': form, 'form_user': form_user})

@login_required
def dashboard_paciente(request):
    # 1. Filtramos los exámenes pertenecientes al paciente actual que estén completados
    # (Ajusta la relación 'orden__expediente__usuario' según tu modelo de usuarios/clientes)
    cliente = Cliente.objects.get(usuario = request.user.id)
    queryset = ExamenRealizado.objects.filter(
        orden__expediente__cliente=cliente, 
        estado='completado'
    ).select_related('orden', 'orden__doctor', 'tipo_examen')

    # 2. Captura y aplicación de los filtros del formulario HTML
    n_orden = request.GET.get('orden')
    medico = request.GET.get('medico')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    if n_orden:
        queryset = queryset.filter(orden__correlativo=n_orden)
    if medico:
        queryset = queryset.filter(orden__doctor__nombreD__icontains=medico)
    if fecha_inicio:
        queryset = queryset.filter(orden__fechaEmision__gte=fecha_inicio)
    if fecha_fin:
        queryset = queryset.filter(orden__fechaEmision__lte=fecha_fin)

    # 3. Estructuración del diccionario con doble nivel de agrupamiento
    ordenes_agrupadas = {}

    for examen in queryset:
        orden_id = examen.orden.id
        
        # Identificamos el laboratorio/sede que procesó este examen a través del usuario analista/recepcionista
        if examen.procesado_por and hasattr(examen.procesado_por, 'sucursal') and examen.procesado_por.sucursal:
            sucursal_id = examen.procesado_por.sucursal.id
            sucursal_nombre = examen.procesado_por.sucursal.nombre # O el campo de texto de tu modelo Sucursal
        else:
            sucursal_id = 0
            sucursal_nombre = "Sede General / Laboratorio Externo"

        # Nivel 1: Si la Orden Médica no existe en el diccionario, la creamos
        if orden_id not in ordenes_agrupadas:
            ordenes_agrupadas[orden_id] = {
                'orden': examen.orden,
                'laboratorios': {} # Diccionario interno para agrupar por sedes independientes
            }

        # Nivel 2: Si la Sede/Laboratorio no existe dentro de esta orden, la creamos
        if sucursal_id not in ordenes_agrupadas[orden_id]['laboratorios']:
            ordenes_agrupadas[orden_id]['laboratorios'][sucursal_id] = {
                'id': sucursal_id,
                'nombre': sucursal_nombre,
                'examenes': []
            }

        # Nivel 3: Añadimos el examen al listado exclusivo de ese laboratorio
        ordenes_agrupadas[orden_id]['laboratorios'][sucursal_id]['examenes'].append(examen)

    context = {
        'ordenes': ordenes_agrupadas.values(),
        'filtros': request.GET 
    }
    return render(request, 'tablero_expediente.html', context)

import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
# ... importa tus cosas de reportlab aquí ...

def generar_pdf_reportlab(examen_id):
    """ Función auxiliar que construye el PDF y devuelve el buffer de memoria """
    buffer = io.BytesIO()
    
    # Aquí va tu lógica actual de ReportLab
    p = canvas.Canvas(buffer)
    p.drawString(100, 100, f"Resultado de Examen ID: {examen_id}")
    # ... renderiza tablas, laboratorios, firmas, etc. ...
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer

@login_required
def ver_pdf_examen(request, examen_id):
    """ Visualiza el PDF en el navegador """
    buffer = generar_pdf_reportlab(examen_id)
    # as_attachment=False hace que se use 'inline'
    return FileResponse(buffer, as_attachment=False, content_type='application/pdf')

@login_required
def descargar_pdf_examen(request, examen_id):
    """ Descarga el PDF directamente """
    buffer = generar_pdf_reportlab(examen_id)
    # as_attachment=True fuerza la descarga
    return FileResponse(
        buffer, 
        as_attachment=True, 
        filename=f"Resultado_Examen_{examen_id}.pdf", 
        content_type='application/pdf'
    )