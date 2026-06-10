from django.http import Http404
from django.shortcuts import render
#importa decorators de validacion
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import *
# Create your views here.

def inventory_home(request):
    return render(request, 'inventory_home.html')

from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Insumo, ItemInventario, MovimientoInventario, CategoriaInsumo
from .forms import InsumoForm, ItemInventarioForm, MovimientoInventarioForm, CategoriaInsumoForm


# ==========================================
# 1. GESTIÓN DEL CATÁLOGO DE INSUMOS
# ==========================================

class InsumoListView(LoginRequiredMixin, ListView):
    """Lista todo el catálogo maestro de insumos clínicos."""
    model = Insumo
    template_name = 'insumo_list.html'
    context_object_name = 'insumos'
    paginate_by = 20


class InsumoCreateView(LoginRequiredMixin, CreateView):
    """Registra un nuevo insumo en el catálogo global."""
    model = Insumo
    form_class = InsumoForm
    template_name = 'insumo_form.html'
    success_url = reverse_lazy('inventario:insumo_list')


class InsumoUpdateView(LoginRequiredMixin, UpdateView):
    """Modifica los datos de un insumo existente."""
    model = Insumo
    form_class = InsumoForm
    template_name = 'insumo_form.html'
    success_url = reverse_lazy('inventario:insumo_list')

# ==========================================
# 2. CONTROL DE STOCK POR SEDE (HÍBRIDO / SEGURO)
# ==========================================

class ItemInventarioListView(LoginRequiredMixin, ListView):
    """Muestra el stock. Los empleados solo ven su sede; los admins/bodegueros ven todo."""
    model = ItemInventario
    template_name = 'item_inventario_list.html'
    context_object_name = 'items'

    def get_queryset(self):
        queryset = ItemInventario.objects.all().select_related('insumo', 'inventario__sede')
        
        # Si el usuario pertenece a una sucursal específica, lo aislamos rigurosamente
        if self.request.user.sucursal:
            return queryset.filter(inventario__sede=self.request.user.sucursal, cantidad__gt=0)
        
        # Si no tiene sucursal (es Admin o Almacenista Central), ve todo el panorama
        return queryset

class ItemInventarioCreateView(LoginRequiredMixin, CreateView):
    """Permite agregar un nuevo insumo a un inventario específico (sede)."""
    model = ItemInventario
    form_class = ItemInventarioForm
    template_name = 'item_inventario_form.html'
    success_url = reverse_lazy('inventario:item_inventario_list')

    def form_valid(self, form):
        inventario = Inventario.objects.get(
            sede=self.request.user.sucursal
        )

        form.instance.inventario = inventario

        return super().form_valid(form)


class ItemInventarioDetailView(LoginRequiredMixin, DetailView):
    """Permite ver el detalle si corresponde a la sede del usuario (o si es Admin)."""
    model = ItemInventario
    template_name = 'item_inventario_detail.html'
    context_object_name = 'item'

    def get_queryset(self):
        queryset = ItemInventario.objects.all()
        # Restricción perimetral por URL
        if self.request.user.sucursal:
            return queryset.filter(inventario__sede=self.request.user.sucursal)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movimientos'] = self.object.movimientos.all().order_by('-fecha_movimiento')[:10]
        return context


# ==========================================
# 3. TRANSACCIONES Y MOVIMIENTOS
# ==========================================

class MovimientoInventarioCreateView(LoginRequiredMixin, CreateView):
    model = MovimientoInventario
    form_class = MovimientoInventarioForm
    template_name = 'movimiento_form.html'
    success_url = reverse_lazy('inventario:item_inventario_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pasamos el usuario con sus roles y sucursal
        return kwargs

    def form_valid(self, form):
        # Doble verificación antes de guardar por si alguien altera el HTML del formulario
        if self.request.user.sucursal and form.cleaned_data['item_inventario'].inventario.sede != self.request.user.sucursal:
            raise Http404("No tienes permisos para alterar el inventario de otra sede.")

        with transaction.atomic():
            movimiento = form.save(commit=False)
            movimiento.usuario = self.request.user
            
            item = movimiento.item_inventario
            if movimiento.tipo_movimiento == 'entrada':
                item.cantidad += movimiento.cantidad
            elif movimiento.tipo_movimiento == 'salida':
                item.cantidad -= movimiento.cantidad
            elif movimiento.tipo_movimiento == 'ajuste':
                item.cantidad = movimiento.cantidad
            
            item.save()
            movimiento.save()
            
        return super().form_valid(form)
