from django.core.management.base import BaseCommand
from usuarios.models import Usuario, Rol, Sucursal
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = "Crea sucursales, roles y usuarios de prueba para cada rol y sucursal"

    def handle(self, *args, **kwargs):

        self.stdout.write("Creando sucursales...")

        sucursal_general, _ = Sucursal.objects.get_or_create(
            nombre="Sucursal General",
            defaults={
                'ubicacion': 'Centro',
                'departamento': 'San Salvador',
                'numero_telefono': '22222222'
            }
        )

        sucursal_especial, _ = Sucursal.objects.get_or_create(
            nombre="Sucursal Especializada",
            defaults={
                'ubicacion': 'Zona Rosa',
                'departamento': 'San Salvador',
                'numero_telefono': '33333333'
            }
        )

        self.stdout.write("Creando roles...")

        rol_lab, _ = Rol.objects.get_or_create(nombre='LAB')
        rol_rec, _ = Rol.objects.get_or_create(nombre='REC')
        rol_inv, _ = Rol.objects.get_or_create(nombre='INV')

        self.stdout.write("Creando grupos...")

        grupo_lab, _ = Group.objects.get_or_create(name='Laboratoristas')
        grupo_rec, _ = Group.objects.get_or_create(name='Recepcionistas')
        grupo_inv, _ = Group.objects.get_or_create(name='Almacenistas')

        self.stdout.write("Creando usuarios...")

        usuarios_a_crear = [
            {
                'username': 'laboratorista1',
                'password': 'lab12345',
                'first_name': 'Juan',
                'last_name': 'Pérez',
                'rol': rol_lab,
                'sucursal': sucursal_general,
                'grupo': grupo_lab,
            },
            {
                'username': 'laboratorista2',
                'password': 'lab12345',
                'first_name': 'Ana',
                'last_name': 'Martínez',
                'rol': rol_lab,
                'sucursal': sucursal_especial,
                'grupo': grupo_lab,
            },
            {
                'username': 'recepcionista1',
                'password': 'rec12345',
                'first_name': 'Maria',
                'last_name': 'González',
                'rol': rol_rec,
                'sucursal': sucursal_general,
                'grupo': grupo_rec,
            },
            {
                'username': 'recepcionista2',
                'password': 'rec12345',
                'first_name': 'Lucía',
                'last_name': 'Ramírez',
                'rol': rol_rec,
                'sucursal': sucursal_especial,
                'grupo': grupo_rec,
            },
            {
                'username': 'almacenista1',
                'password': 'inv12345',
                'first_name': 'Carlos',
                'last_name': 'López',
                'rol': rol_inv,
                'sucursal': sucursal_general,
                'grupo': grupo_inv,
            },
            {
                'username': 'almacenista2',
                'password': 'inv12345',
                'first_name': 'Pedro',
                'last_name': 'Hernández',
                'rol': rol_inv,
                'sucursal': sucursal_especial,
                'grupo': grupo_inv,
            },
        ]

        for datos in usuarios_a_crear:
            if Usuario.objects.filter(username=datos['username']).exists():
                self.stdout.write(f"⚠ Usuario {datos['username']} ya existe, se omite.")
                continue

            usuario = Usuario.objects.create_user(
                username=datos['username'],
                password=datos['password'],
                first_name=datos['first_name'],
                last_name=datos['last_name'],
            )
            usuario.rol = datos['rol']
            usuario.sucursal = datos['sucursal']
            usuario.save()
            usuario.groups.add(datos['grupo'])

            self.stdout.write(f"✔ Usuario {datos['username']} creado.")

        self.stdout.write(self.style.SUCCESS("✔ Usuarios y sucursales cargados correctamente"))
        