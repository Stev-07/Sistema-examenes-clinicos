from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.utils import timezone
import re
from django.core.mail import EmailMessage
from examenes.models import ExamenRealizado, ParametroDefinicion, Resultado
from reportesPDF.views import generar_reporte_completo_pdf
from usuarios.models import *
from usuarios.services.validacion_grupo import grupos_requeridos
from django.db import transaction
from reportesPDF.models import ResultadosExamenesPDF

@login_required
def solicitudes_pendientes(request):
    if not request.user.rol or request.user.rol.nombre != 'LAB':
        return HttpResponseForbidden("No tenés permiso para acceder a esta página.")
    
    buscar = request.GET.get('buscar', '')

    if buscar and not re.fullmatch(r'\d{9}', buscar):
        messages.error(
            request,
            'El DUI debe contener exactamente 9 dígitos numéricos.'
        )

        return render(request, 'pendientes.html', {
            'ordenes': []
        })

    examenes = (
        ExamenRealizado.objects
        .filter( orden__expediente__cliente__n_dui__icontains=buscar, 
                estado='pendiente',
                orden__sucursal=request.user.sucursal)
        .exclude(estado='entregado')
        .select_related(
            'orden',
            'orden__expediente',
            'orden__expediente__cliente__usuario',
            'tipo_examen'
        )
        .order_by('fechaRealizado')
    )

    # Agrupar por orden
    ordenes_dict = {}
    for examen in examenes:
        orden_id = examen.orden.id
        if orden_id not in ordenes_dict:
            ordenes_dict[orden_id] = {
                'orden': examen.orden,
                'examenes': []
            }
        ordenes_dict[orden_id]['examenes'].append(examen)

    # Separar pendientes y completadas
    ordenes_pendientes = []
    ordenes_completadas = []

    for grupo in ordenes_dict.values():
        todos_completados = all(e.estado == 'completado' for e in grupo['examenes'])
        if todos_completados:
            ordenes_completadas.append(grupo)
        else:
            ordenes_pendientes.append(grupo)

    # Pendientes primero, completadas al final
    ordenes = ordenes_pendientes + ordenes_completadas

    return render(request, 'pendientes.html', {
        'ordenes': ordenes
    })


@login_required
@grupos_requeridos('Laboratoristas')
def capturar_resultado(request, examen_id):
    if not request.user.rol or request.user.rol.nombre != 'LAB':
        return HttpResponseForbidden("No tenés permiso para acceder a esta página.")

    examen = get_object_or_404(
        ExamenRealizado.objects.select_related(
            'orden',
            'orden__expediente',
            'orden__expediente__cliente',
            'orden__expediente__cliente__usuario',
            'tipo_examen'
        ),
        id=examen_id
    )

    parametros = ParametroDefinicion.objects.filter(tipo_examen=examen.tipo_examen)

    if request.method == 'POST':
        errores = []
        for parametro in parametros:
            valor = request.POST.get(f"resultado_{parametro.id}", '').strip()
            if not valor:
                errores.append(f"El campo '{parametro.nombreP}' es obligatorio.")
            elif parametro.tipo == 'cuant':
                try:
                    float(valor)
                except ValueError:
                    errores.append(f"El campo '{parametro.nombreP}' debe ser un número.")
            elif parametro.tipo == 'porc':
                try:
                    val = float(valor)
                    if val < 0 or val > 100:
                        errores.append(f"El campo '{parametro.nombreP}' debe estar entre 0 y 100.")
                except ValueError:
                    errores.append(f"El campo '{parametro.nombreP}' debe ser un número.")

        if errores:
            return render(request, 'capturar_resultado.html', {
                'examen': examen,
                'parametros': parametros,
                'errores': errores
            })

        # Si no hay errores guardar
        Resultado.objects.filter(examen_realizado=examen).delete()
        for parametro in parametros:
            valor = request.POST.get(f"resultado_{parametro.id}")
            Resultado.objects.create(
                examen_realizado=examen,
                parametro=parametro,
                valor=valor
            )

        examen.estado = 'completado'
        examen.fechaRealizado = timezone.now()
        examen.procesado_por = get_object_or_404(Usuario, pk = request.user.id)
        examen.save()

        orden = examen.orden
        examenes_de_la_orden = ExamenRealizado.objects.filter(orden=orden)
        todos_completados = examenes_de_la_orden.exclude(estado='completado').count() == 0

        if todos_completados:
            try:
                with transaction.atomic():
                    buffer = generar_reporte_completo_pdf(request, orden)
                    crear_asociacion_resultados_pdf(request, orden)
                correo_paciente = orden.expediente.cliente.correo_electronico
                nombre_paciente = f"{orden.expediente.cliente.usuario.first_name} {orden.expediente.cliente.usuario.last_name}"
                email = EmailMessage(
                    subject=f'Resultados de examen - Orden {orden.correlativo}',
                    body=f'Estimado/a {nombre_paciente},\n\nAdjunto encontrará los resultados de su examen.\n\nSaludos.',
                    to=[correo_paciente],
                )
                email.attach(
                    f'Reporte_Orden_{orden.correlativo}.pdf',
                    buffer.getvalue(),
                    'application/pdf'
                )
                email.send()
                messages.success(request, 'Todos los resultados completados. PDF enviado al correo del paciente.')
            except Exception as e:
                messages.warning(request, f'Resultados guardados pero hubo un error al enviar el correo: {str(e)}')
        else:
            messages.success(request, 'Resultado guardado correctamente.')

        return redirect('resultados:solicitudes_pendientes')

    return render(request, 'capturar_resultado.html', {
        'examen': examen,
        'parametros': parametros
    })

#Para mostrar solamente los exámenes completados
@login_required
def resultados_completados(request):
    if not request.user.rol or request.user.rol.nombre != 'LAB':
        return HttpResponseForbidden("No tenés permiso para acceder a esta página.")

    buscar = request.GET.get('buscar', '')

    if buscar and not re.fullmatch(r'\d{9}', buscar):
        messages.error(
            request,
            'El DUI debe contener exactamente 9 dígitos numéricos.'
        )

        return render(request, 'pendientes.html', {
            'ordenes': []
        })

    examenes = (
        ExamenRealizado.objects
        .filter(
            orden__expediente__cliente__n_dui__icontains=buscar,
            estado='completado',
            orden__sucursal=request.user.sucursal
        )
        .select_related(
            'orden',
            'orden__expediente',
            'orden__expediente__cliente__usuario',
            'tipo_examen'
        )
        .order_by('-fechaRealizado')
    )

    ordenes_dict = {}

    for examen in examenes:
        orden_id = examen.orden.id

        if orden_id not in ordenes_dict:
            ordenes_dict[orden_id] = {
                'orden': examen.orden,
                'examenes': []
            }

        ordenes_dict[orden_id]['examenes'].append(examen)

    ordenes = ordenes_dict.values()

    return render(request, 'resultados_completados.html', {
        'ordenes': ordenes
    })

"""Funcion auxiliar que crea una instancia de resultados para una instancia de orden, si la instancia ya existe la función ya no hace nada"""
def crear_asociacion_resultados_pdf(request, orden_):

    if orden_.reporteGenerado() is True:
        print("SE EJECUTO ACCION SALIDA")
        return 

    ResultadosExamenesPDF.objects.create(
        orden = orden_,
        AnalistaClinico = request.user.registroanalistaclinico,
        expediente = orden_.expediente,
        correlativo = orden_.id
    )
    orden_.reporte_generado = True
    orden_.save()
    print(orden_.reporte_generado)
    print("ASOCIACION CREADA CON EXITO")

    return 