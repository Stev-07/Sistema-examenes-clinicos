# URLs for the inventario app
from django.urls import path
from .views import *

app_name = 'inventario'

urlpatterns = [
    path('', inventory_home, name='inventario_dashboard'),
    # Catálogo de Insumos
    path('insumos/', InsumoListView.as_view(), name='insumo_list'),
    path('insumos/nuevo/', InsumoCreateView.as_view(), name='insumo_create'),
    path('insumos/<int:pk>/editar/', InsumoUpdateView.as_view(), name='insumo_update'),

    # Control de Stock / Existencias por Sede
    path('stock/', ItemInventarioListView.as_view(), name='item_inventario_list'),
    path('stock/<int:pk>/', ItemInventarioDetailView.as_view(), name='item_inventario_detail'),
    path('stock/create/', ItemInventarioCreateView.as_view(), name='item_inventario_create'),

    # Movimientos (Entradas, Salidas, Ajustes)
    path('movimientos/registrar/', MovimientoInventarioCreateView.as_view(), name='movimiento_inventario_create'),
]