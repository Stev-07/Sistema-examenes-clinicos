from django.urls import path
from . import views
urlpatterns = [
    path('create_exp/', views.create_expediente, name='crea_expediente'),
]
