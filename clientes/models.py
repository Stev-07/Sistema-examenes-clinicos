from django.db import models, transaction
from django.utils import timezone
from django.core.validators import MaxValueValidator

# Create your models here.
#opciones para el sexo, solo se admiten 2
class TipoSexo(models.TextChoices):
    masculino = 'M', 'Masculino'
    femenino = 'F', 'Femenino'

class ContadorAnual(models.Model):
    anio = models.PositiveIntegerField(unique=True)
    ultimo_valor = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Contador Anual"
        verbose_name_plural = "Contadores Anuales"

    def __str__(self):
        return f"año: {self.anio}-ultimo: {self.ultimo_valor}"

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    n_dui = models.PositiveBigIntegerField(validators=[MaxValueValidator(999999999)], unique=True)
    fecha_nacimiento = models.DateField()
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
        if not self.numero_expediente:
            self.numero_expediente = self.generar_nuevo_numero_expediente()
        super().save(*args, **kwargs)

    def generar_nuevo_numero_expediente(self):
        anio_actual = timezone.now().year

        #se usa transaccion atomica para evitar que 2 o más procesos se ejecuten al mismo tiempo y generen el mimsmo numero de expediente
        with transaction.atomic():
            contador, created = ContadorAnual.objects.select_for_update().get_or_create(anio = anio_actual)

            #incrementar el contador
            contador.ultimo_valor += 1
            contador.save()

            #formatear el numero de expediente
            nuevo_exp = f"EXP-{anio_actual}-{contador.ultimo_valor:04d}"
            return nuevo_exp


