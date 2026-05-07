from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator
# Create your models here.
#options for models
class TipoRol(models.TextChoices):
    laboratorista = 'LAB', 'laboratorista'
    recepcionista = 'REC', 'recepcionista'
    bodeguero = 'INV', 'almacenista'

class TipoTituloProfesional(models.TextChoices):
    licenciado = 'LIC', 'Licenciatura en Laboratorio Clinico'
    tecnico = 'TEC', 'Tecnico en Laboratorio Clinico'
#clases
class Rol(models.Model):
    nombre = models.CharField(max_length=5, choices=TipoRol.choices)

    def __str__(self):
        return self.get_nombre_display()

#esta clase es empleado
#null a rol por creacion de superusuarios, validar en creacion 
class Usuario(AbstractUser):
    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, null=True, blank=True)

#ESTE MOdelo soportará hasta el JVPLC D3 8 digitos
class RegistroAnalistaClinico(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    acreditacionJVPLC = models.IntegerField(validators=[MaxValueValidator(99999999)])
    tituloProfesional = models.CharField(
        max_length=5, 
        choices=TipoTituloProfesional.choices,
        default=TipoTituloProfesional.licenciado
    )

    def __str__(self):
        return f"{self.usuario.username}-{self.acreditacionJVPLC}"

