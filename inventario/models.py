from django.db import models

# Create your models here.
class Inventario(models.Model):
    sede = models.ForeignKey(
        'usuarios.Sucursal', 
        on_delete=models.CASCADE
    )
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.sede
    
class Insumo(models.Model):
    nombre = models.CharField(max_length=100)
    SKU = models.CharField(
        max_length=50, 
        unique=True
    )
    descripcion = models.TextField(blank=True)

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

    def __str__(self):
        return f"{self.insumo.nombre} - Cantidad: {self.cantidad}"