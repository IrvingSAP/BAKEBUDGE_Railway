from django.db import migrations, models


def marcar_primer_acceso_existentes(apps, schema_editor):
    UserProfile = apps.get_model("accounts", "UserProfile")
    UserProfile.objects.update(primer_acceso_app_completado=True)


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="primer_acceso_app_completado",
            field=models.BooleanField(
                default=False,
                help_text="True tras el primer ingreso a /app/ tras completar seguridad.",
            ),
        ),
        migrations.RunPython(
            marcar_primer_acceso_existentes,
            migrations.RunPython.noop,
        ),
    ]
