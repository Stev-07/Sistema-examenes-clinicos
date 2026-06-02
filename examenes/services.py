from .models import TipoExamen, ExamenRealizado, Resultado

def crear_examenes_desde_orden(orden, tipos_examen_ids):
    for tipo_id in tipos_examen_ids:
        tipo = TipoExamen.objects.get(id=tipo_id)

        examen = ExamenRealizado.objects.create(
            orden=orden,
            tipo_examen=tipo,
            estado='pendiente'
        )

        for parametro in tipo.parametros.all():
            Resultado.objects.create(
                examen_realizado=examen,
                parametro=parametro,
                valor=None
            )