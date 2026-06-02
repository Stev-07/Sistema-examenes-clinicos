from django.urls import path
from . import views

urlpatterns = [
    path('nueva/', views.nueva_orden, name='nueva-orden'),
    path('buscar-cliente/', views.buscar_cliente, name='buscar-cliente'),
    path('buscar-examenes/', views.buscar_examenes, name='buscar-examenes'),
    path('previsualizar-pago/', views.previsualizar_pago, name='previsualizar-pago'),
    path('pago/', views.pago_orden, name='pago-orden'),
    path('confirmar-pago/', views.confirmar_pago, name='confirmar-pago'),

]