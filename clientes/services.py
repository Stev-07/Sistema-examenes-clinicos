from .models import *
from usuarios.models import TipoRol, Rol
from django.db import transaction
from django.contrib.auth.models import Group
#se manejo la logica en 2 forms uno para los datos y otra para los datos de cuenta/login
#luego de relacionar ambos forms, se crea el expediente
#create_expediente_service es excñusivo de la secretaria
@transaction.atomic
def create_expediente_service(form, form_user):
    #asigna el correo como username para el usuario, osea pondrá eso en el campo usuarion en login
    usuario = form_user.save(commit = False)
    usuario.first_name = usuario.first_name.upper()
    usuario.last_name = usuario.last_name.upper()
    usuario.username = form.cleaned_data['correo_electronico']
    usuario.rol = Rol.objects.get(nombre=TipoRol.cliente)
    usuario.sucursal_id = None #no tiene sucursal porque es cliente
    usuario.save()

    paciente = form.save(commit = False)
    paciente.usuario = usuario
    paciente.save()

    expediente = Expediente.objects.create(cliente = paciente)
    expediente.save()

    try:
        grupo_clientes = Group.objects.get(name='Pacientes')
        usuario.groups.add(grupo_clientes)
    except Group.DoesNotExist:
        print("Aviso: El grupo 'Pacientes' no existe en Django. Créalo en el panel de Admin.")  

    context = {
        'paciente': paciente,
        'expediente': expediente,
        'usuario': usuario,
    }
    print(f"se ha creado con exito el usuario y el expediente {expediente.numero_expediente} {usuario.first_name} {usuario.last_name}")
    return context
