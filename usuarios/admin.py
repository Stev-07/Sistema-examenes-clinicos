from django.contrib import admin
from .models import *

#ESTO SIRVE PARA VER Y CREAR OBJETOS EN LA WEB DE ADMINISTRACIÓN
admin.site.register(Usuario)
admin.site.register(RegistroAnalistaClinico)

# Register your models here.
