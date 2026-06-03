from django.contrib import admin
from .models import TipoExamen, ParametroDefinicion, Doctor, Orden, Pagos, ExamenRealizado, Resultado


admin.site.register(TipoExamen)
admin.site.register(ParametroDefinicion)
admin.site.register(Doctor)
admin.site.register(Orden)
admin.site.register(Pagos)
admin.site.register(ExamenRealizado)
admin.site.register(Resultado)
# Register your models here.
