from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('laboratorista/dashboard/', views.laboratorista_dashboard, name='lab-dashboard'),
    path('recepcionista/dashboard/', views.recepcionista_dashboard, name='recepcion-dashboard'),
    path('almacenista/dashboard/', views.almacenista_dashboard, name='inventario-dashboard'),
]