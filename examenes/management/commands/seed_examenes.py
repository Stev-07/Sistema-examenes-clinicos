from django.core.management.base import BaseCommand
from examenes.models import TipoExamen, ParametroDefinicion


class Command(BaseCommand):
    help = "Carga exámenes generales y especiales con sus parámetros"

    def handle(self, *args, **kwargs):

        self.stdout.write("Creando exámenes...")

        # =========================
        # 🧪 EXÁMENES GENERALES
        # =========================

        hemograma = TipoExamen.objects.create(
            nombre="Hemograma completo",
            precio=5.00,
            especial=False,
            perfil="HEMA",
            muestra="sangre_total"
        )

        ParametroDefinicion.objects.bulk_create([
            ParametroDefinicion(
                tipo_examen=hemograma,
                nombreP="Hemoglobina",
                tipo="cuant",
                valorNorma="13 - 17",
                unidadMedida="g/dL"
            ),
            ParametroDefinicion(
                tipo_examen=hemograma,
                nombreP="Hematocrito",
                tipo="cuant",
                valorNorma="40 - 50",
                unidadMedida="%"
            ),
            ParametroDefinicion(
                tipo_examen=hemograma,
                nombreP="Leucocitos",
                tipo="cuant",
                valorNorma="4.5 - 11",
                unidadMedida="x10³/µL"
            ),
        ])

        glucosa = TipoExamen.objects.create(
            nombre="Glucosa en sangre",
            precio=3.00,
            especial=False,
            perfil="QSAN",
            muestra="sangre_total"
        )

        ParametroDefinicion.objects.create(
            tipo_examen=glucosa,
            nombreP="Glucosa",
            tipo="cuant",
            valorNorma="70 - 110",
            unidadMedida="mg/dL"
        )

        urea = TipoExamen.objects.create(
            nombre="Urea",
            precio=3.00,
            especial=False,
            perfil="QSAN",
            muestra="suero"
        )

        ParametroDefinicion.objects.create(
            tipo_examen=urea,
            nombreP="Urea",
            tipo="cuant",
            valorNorma="10 - 50",
            unidadMedida="mg/dL"
        )

        creatinina = TipoExamen.objects.create(
            nombre="Creatinina",
            precio=3.00,
            especial=False,
            perfil="QSAN",
            muestra="suero"
        )

        ParametroDefinicion.objects.create(
            tipo_examen=creatinina,
            nombreP="Creatinina",
            tipo="cuant",
            valorNorma="0.6 - 1.3",
            unidadMedida="mg/dL"
        )

        colesterol = TipoExamen.objects.create(
            nombre="Perfil lipídico",
            precio=8.00,
            especial=False,
            perfil="QSAN",
            muestra="suero"
        )

        ParametroDefinicion.objects.bulk_create([
            ParametroDefinicion(
                tipo_examen=colesterol,
                nombreP="Colesterol total",
                tipo="cuant",
                valorNorma="< 200",
                unidadMedida="mg/dL"
            ),
            ParametroDefinicion(
                tipo_examen=colesterol,
                nombreP="HDL",
                tipo="cuant",
                valorNorma="> 40",
                unidadMedida="mg/dL"
            ),
            ParametroDefinicion(
                tipo_examen=colesterol,
                nombreP="LDL",
                tipo="cuant",
                valorNorma="< 100",
                unidadMedida="mg/dL"
            ),
        ])

        # =========================
        # 🧬 EXÁMENES ESPECIALES
        # =========================

        tsh = TipoExamen.objects.create(
            nombre="Perfil tiroideo",
            precio=20.00,
            especial=True,
            perfil="ENDO",
            muestra="suero"
        )

        ParametroDefinicion.objects.bulk_create([
            ParametroDefinicion(
                tipo_examen=tsh,
                nombreP="TSH",
                tipo="cuant",
                valorNorma="0.4 - 4.0",
                unidadMedida="µUI/mL"
            ),
            ParametroDefinicion(
                tipo_examen=tsh,
                nombreP="T3",
                tipo="cuant",
                valorNorma="80 - 200",
                unidadMedida="ng/dL"
            ),
        ])

        vih = TipoExamen.objects.create(
            nombre="VIH (ELISA)",
            precio=25.00,
            especial=True,
            perfil="INMU",
            muestra="suero"
        )

        ParametroDefinicion.objects.create(
            tipo_examen=vih,
            nombreP="VIH",
            tipo="cuali",
            valorNorma="No reactivo",
            unidadMedida="-"
        )

        hba1c = TipoExamen.objects.create(
            nombre="Hemoglobina glicosilada (HbA1c)",
            precio=18.00,
            especial=True,
            perfil="ENDO",
            muestra="sangre_total"
        )

        ParametroDefinicion.objects.create(
            tipo_examen=hba1c,
            nombreP="HbA1c",
            tipo="porc",
            valorNorma="< 5.7",
            unidadMedida="%"
        )

        self.stdout.write(self.style.SUCCESS("✔ Exámenes cargados correctamente"))