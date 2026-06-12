from django.db import models
from reportesPDF.models import ConfiguracionReporte
from django.db import models

class TiposPerfil(models.TextChoices):
    QUIMICA_SANGUINEA = 'QSAN', 'QUIMICA SANGUÍNEA'
    QUIMICA_URINARIA = 'QURI', 'QUIMICA URINARIA'
    ELECTROLITOS = 'ELEC', 'ELECTROLITOS'
    HEMATOLOGIA = 'HEMA', 'HEMATOLOGIA'
    COAGULACION = 'COAG', 'COAGULACIÓN'
    ENDOCRINOLOGIA = 'ENDO', 'ENDOCRINOLOGÍA'
    INMUNOLOGIA = 'INMU', 'INMUNOLOGÍA'
    MICROBIOLOGIA = 'MICR', 'MICROBIOLOGÍA'
    PRUEBAS_ESPECIALES = 'PESP', 'PRUEBAS ESPECIALES'
    MARCADORES_TUMORALES = 'MTUM', 'MARCADORES TUMORALES'
    MARCADORES_CARDIACOS = 'MCAR', 'MARCADORES CARDÍACOS'
    NIVELES_SERICOS = 'NSRE', 'NIVELES SÉRICOS'
    BIOLOGIA_MOLECULAR = 'BMOL', 'BIOLOGÍA MOLECULAR'
    UROANALISIS = 'UROA', 'UROANÁLISIS'
    COPROLOGIA = 'COPR', 'COPROLOGÍA'
    DROGAS_ORINA = 'DORO', 'DROGAS EN ORINA'
    DROGAS_TERAPEUTICAS = 'DTER', 'DROGAS TERAPÉUTICAS'
    INMUNOGLOBULINAS = 'IMGL', 'INMUNOGLOBULINAS'

#CLASE PARA TIPO DE PARAMETROS
#ANTEPOSICIÓN Y = SI, N = NO, C = CRITICO
class TipoResultado(models.TextChoices):
    POSITIVO = "POSIT", "Positivo"
    NEGATIVO = "NEGAT", "Negativo"
    REACTIVO = "YREAC", "Reactivo"
    NO_REACTIVO = "NREAC", "No Reactivo"
    DETECTADO = "YDETE", "Detectado"
    NO_DETECTADO = "NDETE", "No Detectado"
    PRESENTE = "PRESE", "Presente"
    AUSENTE = "AUSEN", "Ausente"
    NORMAL = "NORMA", "Normal"
    ANORMAL = "ANORM", "Anormal"
    ALTO = "ALTO", "Alto"
    BAJO = "BAJO", "Bajo"
    CRITICO_ALTO = "CALTO", "Crítico Alto"
    CRITICO_BAJO = "CBAJO", "Crítico Bajo"
    TRAZA = "TRAZA", "Traza"
    ESCASO = "ESCAS", "Escaso"
    MODERADO = "MODER", "Moderado"
    ABUNDANTE = "ABUND", "Abundante"
    INDETERMINADO = "INDET", "Indeterminado"

TIPO_MUESTRA = [
    ('suero', 'Suero'),
    ('plasma', 'Plasma'),
    ('sangre_total', 'Sangre Total'),
    ('sangre_capilar', 'Sangre Capilar'),
    ('orina', 'Orina'),
    ('orina_24h', 'Orina 24 Horas'),
    ('heces', 'Heces'),
    ('esputo', 'Esputo'),
    ('semen', 'Semen'),
    ('hisopado_faringeo', 'Hisopado Faríngeo'),
    ('hisopado_nasal', 'Hisopado Nasal'),
    ('exudado_vaginal', 'Exudado Vaginal'),
    ('exudado_uretral', 'Exudado Uretral'),
    ('secrecion_herida', 'Secreción de Herida'),
    ('lcr', 'Líquido Cefalorraquídeo'),
    ('liquido_pleural', 'Líquido Pleural'),
    ('liquido_peritoneal', 'Líquido Peritoneal'),
    ('liquido_sinovial', 'Líquido Sinovial'),
    ('biopsia', 'Biopsia'),
    ('otro', 'Otro'),
]
# Clase con la que se definirán los parámetros de los exámenes
# Clase con la que se definirán los exámenes con sus respectivos datos
class TipoExamen(models.Model):
    #CORRECIÓN
    nombre = models.CharField(max_length=100, null=False, blank=False)
    precio = models.DecimalField(max_digits=8, decimal_places=2, null=False, blank=False)
    especial = models.BooleanField(default=False)
    perfil = models.CharField(max_length=100, choices=TiposPerfil.choices, null=True, blank=True)
    muestra = models.CharField(
        max_length=20, 
        choices=TIPO_MUESTRA, 
        null=True, 
        blank=True,
        default='suero'
    )

    def __str__(self):
        return self.nombre
    
# Va primero porque TipoExamen la referencia
class ParametroDefinicion(models.Model):
    #ESTE PARAMÉTRO APUNTA A SU UNICO EXAMEN 
    tipo_examen = models.ForeignKey(TipoExamen, on_delete=models.PROTECT, related_name='parametros')
    nombreP = models.CharField(max_length=100, null=False, blank=False)
    tipo_choices = [
        ('cuant', 'CUANTITATIVO'),
        ('cuali', 'CUALITATIVO'),
        ('porc', 'PORCENTUAL'),
        ('otros', 'OTROS')
    ]
    tipo = models.CharField(
        max_length=10,
        null=True,
        blank=False,
        choices=tipo_choices,
        default='cuant'
    )
    valorNorma = models.CharField(max_length=25, null=False, blank=False)
    unidadMedida = models.CharField(max_length=25, null=False, blank=False)

    def __str__(self):
        return self.nombreP

# Clase en la que se definirán los doctores para la realización de órdenes
class Doctor(models.Model):
    nombreD = models.CharField(max_length=100, null=False, blank=False)
    jvpm = models.IntegerField()

    def __str__(self):
        return f"{self.nombreD} - JVPM: {self.jvpm}"

# En esta clase se define lo que es la orden
#por cada instancia de orden, debe existir un reporte generado
class Orden(models.Model):
    expediente = models.ForeignKey('clientes.Expediente', on_delete=models.PROTECT)
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT)
    correlativo = models.IntegerField(null=False, blank=False)
    fechaEmision = models.DateField(auto_now_add=False)
    reporte_generado = models.BooleanField(default=False)

    def __str__(self):
        return f"Orden {self.correlativo} - {self.expediente}"
    
    def reporteGenerado(self):
        return self.reporte_generado

#Clase de pago para registrar los pagos 
class Pagos(models.Model):
    orden = models.OneToOneField(Orden, on_delete= models.CASCADE)
    monto = models.DecimalField(max_digits=8, decimal_places=2, null=False, blank=False)
    fecha = models.DateTimeField(auto_now_add=True)
    completado = models.BooleanField(default=False)
    tipo_pago = models.CharField(max_length=20, null=False, blank=False)

    def __str__(self):
        return f"Pago {self.orden.id} - ${self.monto} - {self.tipo_pago}"
    
#Clase para decir si el examen realizado 
class ExamenRealizado(models.Model): 
    #Cada examen realizado pertenece a una orden, teniendo una orden 1 o muchos examenes realizados
    orden = models.ForeignKey(Orden, on_delete= models.PROTECT) 
    tipo_examen = models.ForeignKey(TipoExamen, on_delete=models.PROTECT)
    fechaRealizado = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    #Para que estado no sea un campo libre lo haremos mediante un choices
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En proceso'),
        ('completado', 'Completado'),
        ('entregado', 'Entregado'),

    ]
    estado = models.CharField(max_length=25, choices=ESTADO_CHOICES, default='pendiente')
    observaciones = models.CharField(max_length=500, null= True, blank=True)
    #Atributo para relacionar el usuario (la recepcionista) que realicé el proceso
    procesado_por = models.ForeignKey('usuarios.Usuario', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Examen realizado #{self.id}-nombre: {self.tipo_examen.nombre} - Orden: {self.orden.correlativo} - Estado: {self.estado}"

#Clase para el resultado 
class Resultado(models.Model): 
    examen_realizado = models.ForeignKey(ExamenRealizado, on_delete= models.CASCADE, related_name='resultados')
    parametro = models.ForeignKey(ParametroDefinicion, on_delete= models.PROTECT)
    valor = models.CharField(max_length=50, null=True, blank =True )

    def __str__(self):
        return f"{self.parametro.nombreP}: {self.valor}"
    #PODER CREAR UN EXÁMEN, CREARLE SUS PARAMÉTROS, CREAR UN RESULTADO EXAMEN Y UN RESULTADO PARAMETROD
    #QUE SE RELACIONEN ENTRE ELLOS CON SUS RESPETIVAS LALVES ETC, Y SE DEBEN PDOER TENER 
    #SUS RELACIONES

    