# URLs for the inventario app
from django.urls import path
from .views import *

app_name = 'inventario'
urlpatterns = [
    path('', inventory_home, name='inventory_home'),
]