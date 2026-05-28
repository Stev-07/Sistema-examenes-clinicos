from django.db import models, transaction
from django.utils import timezone
from datetime import date
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

# Create your models here.
#Funciones de validadion 

#compara el año de nacimiento y al actual le resta 115, si el año es menor lanza error
def validar_anio_nacimiento(fecha):
    hoy = timezone.localdate()
    try:
        fecha_limite = hoy.replace(year=hoy.year - 115)
    except ValueError:
        # Maneja el caso raro de un 29 de febrero hace 115 años
        fecha_limite = hoy.replace(year=hoy.year - 115, day=28)

    if fecha < fecha_limite:
        raise ValidationError("La fecha de nacimiento no puede ser anterior a 115 años")

solo_numeros = RegexValidator(
    regex = r'^\d{9}$',
    message= "El número de DUI debe contener exactamente 9 digitos numericos",
    code="DUI INVALIDO"
)

#opciones para el sexo, solo se admiten 2
class TipoSexo(models.TextChoices):
    MASCULINO = 'M', 'Masculino'
    FEMENINO = 'F', 'Femenino'

class ContadorAnual(models.Model):
    anio = models.PositiveIntegerField(unique=True)
    ultimo_valor = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Contador Anual"
        verbose_name_plural = "Contadores Anuales"

    def __str__(self):
        return f"año: {self.anio}-ultimo: {self.ultimo_valor}"

class Cliente(models.Model):
    usuario = models.OneToOneField('usuarios.Usuario', on_delete=models.CASCADE, related_name='cliente_perfil')
    n_dui = models.CharField(max_length=9, unique=True, validators=[solo_numeros])
    fecha_nacimiento = models.DateField(validators=[validar_anio_nacimiento])
    correo_electronico = models.EmailField(unique=True)
    sexo = models.CharField(max_length=1, choices=TipoSexo.choices)

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.n_dui}"   

class Expediente(models.Model):
    numero_expediente = models.CharField(
        max_length=20,
        unique=True,
        blank=False,
        null=False,
        editable=False,
        help_text="Generado automáticamente"
    )
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE, related_name='expediente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Expediente de {self.cliente.nombre} {self.cliente.apellido}"
    
    def save(self, *args, **kwargs):
        # guardado atómico o pasa todo o nada
        with transaction.atomic():
            if not self.numero_expediente:
                self.numero_expediente = self.generar_nuevo_numero_expediente()
                
            self.full_clean()
            super().save(*args, **kwargs)

    def generar_nuevo_numero_expediente(self):
            anio_actual = timezone.now().year

            # Bloquea la fila del contador para evitar que haya dow expedientes con el mismo correlativo
            contador, created = ContadorAnual.objects.select_for_update().get_or_create(anio=anio_actual)
            contador.ultimo_valor += 1
            contador.save()

            return f"EXP-{anio_actual}-{contador.ultimo_valor:04d}"


