from django.db import models


class CategoriaInsumo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Inventario(models.Model):
    nombreInventario = models.CharField(
        max_length=100, 
        unique=True,
        default='Inventario principal'
    )
    #SEDE ser refiere al laboratorio, no sucursales
    sede = models.ForeignKey(
        'usuarios.Sucursal',
        on_delete=models.PROTECT
    )
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.sede.nombre


class Insumo(models.Model):

    UNIDAD_MEDIDA = [
        ('unidad', 'Unidad'),
        ('caja', 'Caja'),
        ('frasco', 'Frasco'),
        ('kit', 'Kit'),
        ('ml', 'Mililitros'),
        ('l', 'Litros'),
        ('g', 'Gramos'),
        ('mg', 'Miligramos'),
        ('tubo', 'Tubo'),
        ('otro', 'Otro'),
    ]

    nombre = models.CharField(max_length=100)

    SKU = models.CharField(
        max_length=50,
        unique=True
    )

    descripcion = models.TextField(blank=True)

    categoria = models.ForeignKey(
        CategoriaInsumo,
        on_delete=models.PROTECT,
        related_name='insumos',
        null=True,
        blank=True
    )

    unidad_medida = models.CharField(
        max_length=20,
        choices=UNIDAD_MEDIDA,
        default='unidad'
    )

    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({self.SKU})"


class ItemInventario(models.Model):
    insumo = models.ForeignKey(
        Insumo,
        on_delete=models.CASCADE,
        related_name='items'
    )

    inventario = models.ForeignKey(
        Inventario,
        on_delete=models.CASCADE,
        related_name='insumos'
    )

    cantidad = models.PositiveIntegerField(default=0)

    stock_minimo = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('insumo', 'inventario')

    def __str__(self):
        return f"{self.insumo.nombre}-{self.insumo.SKU}- Cantidad: {self.cantidad}"

    @property
    def bajo_stock(self):
        return self.cantidad <= self.stock_minimo


class MovimientoInventario(models.Model):

    TIPO_MOVIMIENTO = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
    ]

    item_inventario = models.ForeignKey(
        ItemInventario,
        on_delete=models.PROTECT,
        related_name='movimientos'
    )

    tipo_movimiento = models.CharField(
        max_length=10,
        choices=TIPO_MOVIMIENTO
    )

    cantidad = models.PositiveIntegerField()

    observacion = models.TextField(
        blank=True,
        null=True
    )

    usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    fecha_movimiento = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.get_tipo_movimiento_display()} - "
            f"{self.item_inventario.insumo.nombre} - "
            f"{self.cantidad}"
        )