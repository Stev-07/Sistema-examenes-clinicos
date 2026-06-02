from django.shortcuts import render,redirect
from django.contrib import messages
from .forms import *
from .services import *

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

def dashboard_paciente(request):
    return render(request, 'dashboard_paciente.html')