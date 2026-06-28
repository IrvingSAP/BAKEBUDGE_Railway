from django.db import migrations

MONEDAS = [
    {"codigo": "COP", "nombre": "Peso colombiano", "simbolo": "$", "decimales": 0, "activa": True, "orden": 1},
    {"codigo": "USD", "nombre": "Dólar estadounidense", "simbolo": "US$", "decimales": 2, "activa": True, "orden": 2},
    {"codigo": "MXN", "nombre": "Peso mexicano", "simbolo": "$", "decimales": 2, "activa": True, "orden": 3},
    {"codigo": "EUR", "nombre": "Euro", "simbolo": "€", "decimales": 2, "activa": True, "orden": 4},
    {"codigo": "ARS", "nombre": "Peso argentino", "simbolo": "$", "decimales": 2, "activa": True, "orden": 5},
    {"codigo": "CLP", "nombre": "Peso chileno", "simbolo": "$", "decimales": 0, "activa": True, "orden": 6},
    {"codigo": "PEN", "nombre": "Sol peruano", "simbolo": "S/", "decimales": 2, "activa": True, "orden": 7},
    {"codigo": "VEN", "nombre": "Bolivar Venezolano", "simbolo": "Bs.S/", "decimales": 2, "activa": True, "orden": 8},
]


def seed_monedas(apps, schema_editor):
    Moneda = apps.get_model("core", "Moneda")
    for row in MONEDAS:
        Moneda.objects.update_or_create(codigo=row["codigo"], defaults=row)


def unseed_monedas(apps, schema_editor):
    Moneda = apps.get_model("core", "Moneda")
    Moneda.objects.filter(codigo__in=[row["codigo"] for row in MONEDAS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_monedas, unseed_monedas),
    ]
