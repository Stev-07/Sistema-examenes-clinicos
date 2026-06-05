from django.contrib import admin

# Register your models here.
from .models import ResultadosExamenesPDF, ConfiguracionReporte

admin.site.register(ResultadosExamenesPDF)
admin.site.register(ConfiguracionReporte)