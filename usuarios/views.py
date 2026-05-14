from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

#login, redirige según grupo al que pertenece usuario
def login_view(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        print("datos recibidos:", form.data)  # Debug: Verificar datos recibidos

        if not form.is_valid():
            print("Errores del formulario:", form.errors)  # Debug: Verificar errores del formulario    
        if form.is_valid():
            print("formulario valido")
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

# Debug: Verificar credenciales antes de autenticación
            print(f"Intentando autenticar usuario: {username} con contraseña: {'*' * len(password)}")  # Oculta la contraseña en los logs   
            user = authenticate(
                request,
                username = username,
                password = password
            )
            #print user para debug
            print("Usuario autenticado:", user)  # Debug: Verificar usuario autenticado
            print("Grupos del usuario:", user.groups.all())  # Debug: Verificar grupos del usuario

            if user is not None:
                login(request, user)
                #redireccionar según rol
                if user.groups.filter(name='Laboratoristas').exists():
                    return redirect('lab-dashboard')
                elif user.groups.filter(name='recepcion-dashboard').exists():
                    return redirect('recepcionista_dashboard')
                elif user.groups.filter(name='Almacenistas').exists():
                    return redirect('inventario-dashboard')
                else:
                    return redirect('login')  # Redirige al login si el usuario no tiene un rol asignado
            else:
                form.add_error(None, 'Credenciales inválidas')

    return render(request, './login.html', {'form': form})

@login_required
def laboratorista_dashboard(request):
    return HttpResponse("Bienvenido al dashboard del laboratorista")

def recepcionista_dashboard(request):
    return HttpResponse("Bienvenido al dashboard del recepcionista")        

def almacenista_dashboard(request): 
    return HttpResponse("Bienvenido al dashboard del almacenista")    



# Create your views here.
