from django import forms
from .models import CategoriaInsumo, Inventario, Insumo, ItemInventario, MovimientoInventario
from django_select2 import forms as s2forms

class InsumoSelect2Widget(s2forms.ModelSelect2Widget):
    """Widget de búsqueda para el catálogo global de Insumos."""
    model = Insumo
    search_fields = [
        'nombre__icontains',
        'SKU__icontains',
    ]

class ItemInventarioSelect2Widget(s2forms.ModelSelect2Widget):
    """Widget de búsqueda para Items de Inventario filtrados por permisos."""
    model = ItemInventario
    search_fields = [
        'insumo__nombre__icontains',  # Busca a través de la relación con Insumo
    ]

    def get_queryset(self):
        """
        Este método es vital para Select2. Filtra lo que el usuario ve en tiempo real 
        cuando empieza a escribir en la barra de búsqueda AJAX.
        """
        request = getattr(self, 'request', None)
        
        if request and request.user.is_authenticated:
            user = request.user
            if user.sucursal:
                # Si el usuario pertenece a una sede, solo busca items de su sede
                return ItemInventario.objects.filter(inventario__sede=user.sucursal)
            elif user.is_staff or (user.rol and user.rol.nombre == 'INV'):
                # Si es administrador o rol INV, busca en todo el universo de items
                return ItemInventario.objects.all()
                
        return ItemInventario.objects.none()

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
            'insumo': InsumoSelect2Widget(attrs={
                'class': 'inv-form-control', 
                'style': 'width: 100%;',
                'data-placeholder': 'Escriba el nombre del insumo...'
            }),
            'cantidad': forms.NumberInput(attrs={'class': 'inv-form-control', 'min': 0}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'inv-form-control', 'min': 0}),
        }


class MovimientoInventarioForm(forms.ModelForm):
    class Meta:
        model = MovimientoInventario
        fields = ['item_inventario', 'tipo_movimiento', 'cantidad', 'observacion']
        widgets = {
            # se utiliza select2 libreria 
            'item_inventario': ItemInventarioSelect2Widget(attrs={
                'class': 'inv-form-control', 
                'style': 'width: 100%;',
                'data-placeholder': 'Escriba para buscar el item en inventario...'
            }),
            'tipo_movimiento': forms.Select(attrs={'class': 'inv-form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'inv-form-control', 'min': 1}),
            'observacion': forms.Textarea(attrs={'rows': 3, 'class': 'inv-form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        request_obj = kwargs.pop('request', None)
        
        super().__init__(*args, **kwargs)
        
        # se asigna el request al widget de Select2 para que pueda filtrar por AJAX
        if request_obj:
            self.fields['item_inventario'].widget.request = request_obj

        if user:
            if user.sucursal:
                # Empleado de sucursal: Filtrado estricto
                self.fields['item_inventario'].queryset = ItemInventario.objects.filter(
                    inventario__sede=user.sucursal
                )
            elif user.is_staff or (user.rol and user.rol.nombre == 'INV'):
                self.fields['item_inventario'].queryset = ItemInventario.objects.all()

    def clean(self):
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