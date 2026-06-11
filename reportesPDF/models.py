from django.db import models

# Create your models here.
class ResultadosExamenesPDF(models.Model):
    orden = models.ForeignKey(
        'examenes.Orden',
        on_delete=models.PROTECT,
    )
    AnalistaClinico = models.ForeignKey(
        'usuarios.RegistroAnalistaClinico',
        on_delete=models.PROTECT,
    )
    expediente = models.ForeignKey(
        'clientes.Expediente',
        on_delete=models.CASCADE,
        related_name='all_resultados_pdf'
    )
    fecha_emision = models.DateTimeField(auto_now_add=True)
    correlativo = models.CharField(max_length=50)
    encabezado = models.CharField(
        max_length=600, 
        null=True, 
        blank=True
    )

    def __str__(self):
        return f"Resultados PDF para Orden {self.orden.correlativo}"
    
class ConfiguracionReporte(models.Model):

    TIPOS = [
        ('TABLA', 'Tabla'),
        ('CATEGORIZADO', 'Categorizado'),
        ('IMAGEN', 'Imagen')
    ]

    #examen = models.ForeignKey(
    #   'examenes.Examen',
    #  on_delete=models.CASCADE
    #)
    # Relación directa con el tipo de examen
    tipo_examen = models.ForeignKey(
        'examenes.TipoExamen', 
        on_delete=models.CASCADE,
        related_name='configuracion'
    ) 

    tipo = models.CharField(
        max_length=20,
        choices=TIPOS
    )

    def __str__(self):
        return f"Configuración para {self.tipo_examen.nombre}: {self.tipo}"