from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('laboratorista/dashboard/', views.laboratorista_dashboard, name='lab-dashboard'),
    path('recepcionista/dashboard/', views.recepcionista_dashboard, name='recepcion-dashboard'),
    path('almacenista/dashboard/', views.almacenista_dashboard, name='inventario-dashboard'),
]