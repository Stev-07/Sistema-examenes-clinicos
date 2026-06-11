from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST
from clientes.models import Cliente, Expediente
from .models import TipoExamen, Orden, Doctor, Pagos, ExamenRealizado
from .forms import DoctorForm, OrdenForm

#Verificamos el rol del usuario al ingresar para gestionar los exámenes
@login_required
def nueva_orden(request):
    if not request.user.rol or request.user.rol.nombre != 'REC':
        return HttpResponseForbidden("No tenés permiso para acceder a esta página.")
    
    doctor_form = DoctorForm()
    orden_form = OrdenForm()
    
    return render(request, 'nueva_solicitud.html', {
        'doctor_form': doctor_form,
        'orden_form': orden_form,
    })

#FUNCIÓN PARA REALIZAR LA BÚSQUEDA DE UN CLIENTE SEGÚN SU DUI
@login_required
@require_POST
def buscar_cliente(request):
    dui = request.POST.get('dui', '')
    try:
        cliente = Cliente.objects.get(n_dui=dui)
        expediente = cliente.expediente
        return JsonResponse({
            'encontrado': True,
            'nombre': f"{cliente.usuario.first_name} {cliente.usuario.last_name}",
            'expediente_id': expediente.id,
            'numero_expediente': expediente.numero_expediente,
        })
    except Cliente.DoesNotExist:
        return JsonResponse({'encontrado': False})
    except Expediente.DoesNotExist:
        return JsonResponse({'encontrado': False, 'error': 'El cliente no tiene expediente'})

#FUNCIÓN PARA FILTRAR LOS EXÁMENES SEGÚN EL TIPO DE SUCURSAL
@login_required
@require_POST
def buscar_examenes(request):
    query = request.POST.get('q', '')
    sucursal = request.user.sucursal
    if 'especializada' in sucursal.nombre.lower():
        especial = True
    else:
        especial = False
    examenes = TipoExamen.objects.filter(nombre__icontains=query, especial=especial)
    data = [{'id': e.id, 'nombre': e.nombre, 'precio': str(e.precio)} for e in examenes]
    return JsonResponse({'examenes': data})

#FUNCIÓN PARA GUARDAR DE FORMA MOMENTANEA LOS DATOS MIENTRAS SE REALIZA EL PAGO
@login_required
@require_POST
def previsualizar_pago(request):
    if not request.user.rol or request.user.rol.nombre != 'REC':
        return HttpResponseForbidden("No tenés permiso para acceder a esta página.")
    
    doctor_form = DoctorForm(request.POST)
    orden_form = OrdenForm(request.POST)

    if doctor_form.is_valid() and orden_form.is_valid():
        request.session['orden_pendiente'] = {
            'expediente_id': request.POST.get('expediente_id'),
            'examenes_ids': request.POST.getlist('examenes'),
            'nombre_doctor': doctor_form.cleaned_data['nombreD'],
            'jvpm': doctor_form.cleaned_data['jvpm'],
            'correlativo': orden_form.cleaned_data['correlativo'],
            'fechaEmision': str(orden_form.cleaned_data['fechaEmision']),
            'total': str(orden_form.cleaned_data['total']),
        }
        return redirect('pago-orden')
    
    # Si los formularios no son validos regresa a la página de nueva_solicitud.html 
    #y manda los errores de validación al template para que se los muestre al usuario 
    #Así si algún campo queda vacío se detecta el error sin perder los demás datos

    return render(request, 'nueva_solicitud.html', {
        'doctor_form': doctor_form,
        'orden_form': orden_form,
        'errores': True
    })

#FUNCIÓN PARA REALIZAR EL PAGO 
@login_required
def pago_orden(request):
    if not request.user.rol or request.user.rol.nombre != 'REC':
        return HttpResponseForbidden("No tenés permiso para acceder a esta página.")
    
    orden_pendiente = request.session.get('orden_pendiente')
    if not orden_pendiente:
        return redirect('nueva-orden')
    
    return render(request, 'pago_orden.html', {'total': orden_pendiente['total']})

#FUNCIÓN PARA REALIZAR PAGO 
@login_required
@require_POST
def confirmar_pago(request):
    if not request.user.rol or request.user.rol.nombre != 'REC':
        return HttpResponseForbidden("No tenés permiso para acceder a esta página.")
    
    orden_pendiente = request.session.get('orden_pendiente')
    if not orden_pendiente:
        return redirect('nueva-orden')
    
    try:
        tipo_pago = request.POST.get('tipo_pago')

        expediente = Expediente.objects.get(id=orden_pendiente['expediente_id'])
        doctor, _ = Doctor.objects.get_or_create(
            jvpm=orden_pendiente['jvpm'],
            defaults={'nombreD': orden_pendiente['nombre_doctor']}
        )

        orden = Orden.objects.create(
            expediente=expediente,
            doctor=doctor,
            correlativo=orden_pendiente['correlativo'],
            fechaEmision=orden_pendiente['fechaEmision'],
        )

        for examen_id in orden_pendiente['examenes_ids']:
            examen = TipoExamen.objects.get(id=examen_id)
            ExamenRealizado.objects.create(
                orden=orden,
                tipo_examen=examen,
                procesado_por=request.user
        )

        Pagos.objects.create(
        orden=orden,
        monto=orden_pendiente['total'],
        tipo_pago=tipo_pago,
        completado=True
        )

        del request.session['orden_pendiente']
        return redirect('nueva-orden')

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
