from django.urls import path
from . import views
urlpatterns = [
    path('create_exp/', views.create_paciente_expediente, name='crea_expediente'),
]
