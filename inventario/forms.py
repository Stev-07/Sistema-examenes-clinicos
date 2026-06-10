from django import forms
from .models import CategoriaInsumo, Inventario, Insumo, ItemInventario, MovimientoInventario


class CategoriaInsumoForm(forms.ModelForm):
    """Formulario para crear y editar las categorías de los insumos clínicos."""
    class Meta:
            model = CategoriaInsumo
            fields = ['nombre', 'descripcion', 'activo']
            widgets = {
                'nombre': forms.TextInput(attrs={'class': 'inv-form-control'}),
                'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'inv-form-control'}),
                'activo': forms.CheckboxInput(attrs={'class': 'inv-checkbox'}),
            }


class InventarioForm(forms.ModelForm):
    """Formulario para asignar un inventario general a una sucursal/sede."""
    class Meta:
            model = Inventario
            fields = ['sede']
            widgets = {
                'sede': forms.Select(attrs={'class': 'inv-form-control'}),
            }


class InsumoForm(forms.ModelForm):
    """Formulario para el catálogo maestro de insumos, reactivos o materiales."""
    class Meta:
            model = Insumo
            fields = ['nombre', 'SKU', 'descripcion', 'categoria', 'unidad_medida', 'activo']
            widgets = {
                'nombre': forms.TextInput(attrs={'class': 'inv-form-control'}),
                'SKU': forms.TextInput(attrs={'class': 'inv-form-control'}),
                'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'inv-form-control'}),
                'categoria': forms.Select(attrs={'class': 'inv-form-control'}),
                'unidad_medida': forms.Select(attrs={'class': 'inv-form-control'}),
                'activo': forms.CheckboxInput(attrs={'class': 'inv-checkbox'}),
            }


class ItemInventarioForm(forms.ModelForm):
    """Formulario para vincular un insumo a un inventario específico y definir alertas."""
    class Meta:
            model = ItemInventario
            fields = ['insumo', 'cantidad', 'stock_minimo']
            widgets = {
                'insumo': forms.Select(attrs={'class': 'inv-form-control'}),
                'cantidad': forms.NumberInput(attrs={'class': 'inv-form-control', 'min': 0}),
                'stock_minimo': forms.NumberInput(attrs={'class': 'inv-form-control', 'min': 0}),
            }


class MovimientoInventarioForm(forms.ModelForm):
    class Meta:
            model = MovimientoInventario
            fields = ['item_inventario', 'tipo_movimiento', 'cantidad', 'observacion']
            widgets = {
                'item_inventario': forms.Select(attrs={'class': 'inv-form-control'}),
                'tipo_movimiento': forms.Select(attrs={'class': 'inv-form-control'}),
                'cantidad': forms.NumberInput(attrs={'class': 'inv-form-control', 'min': 1}),
                'observacion': forms.Textarea(attrs={'rows': 3, 'class': 'inv-form-control'}),
            }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            if user.sucursal:
                # Empleado de sucursal: Filtrado estricto
                self.fields['item_inventario'].queryset = ItemInventario.objects.filter(
                    inventario__sede=user.sucursal
                )
            elif user.is_staff or (user.rol and user.rol.nombre == 'INV'):
                # Es súper usuario o un bodeguero/almacenista general: Ve todo para distribuir
                self.fields['item_inventario'].queryset = ItemInventario.objects.all()

    def clean(self):
        # (La validación de limpieza que ya tenías se mantiene exactamente igual)
        cleaned_data = super().clean()
        tipo_movimiento = cleaned_data.get('tipo_movimiento')
        cantidad = cleaned_data.get('cantidad')
        item_inventario = cleaned_data.get('item_inventario')

        if tipo_movimiento == 'salida' and item_inventario and cantidad:
            if item_inventario.cantidad < cantidad:
                self.add_error(
                    'cantidad', 
                    f"Stock insuficiente. Disponible: {item_inventario.cantidad} unidades."
                )
        return cleaned_data