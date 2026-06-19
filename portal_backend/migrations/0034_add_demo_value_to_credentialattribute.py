from django.db import migrations, models


DEMO_VALUES = {
    "rekeninghouder": "Jan de Vries",
    "bankrekening": "NL91ABNA0417164300",
    "uitgever": "De Hollandsche Bank",
    "datum_uitgifte": "01-01-2024",
    "inkomensprofiel_gelijk": "Ja",
}


def seed_bank_income_profile_demo_values(apps, schema_editor):
    CredentialAttribute = apps.get_model("portal_backend", "CredentialAttribute")
    for tag, value in DEMO_VALUES.items():
        CredentialAttribute.objects.filter(credential_attribute_tag=tag).update(
            demo_value=value
        )


class Migration(migrations.Migration):
    dependencies = [
        ("portal_backend", "0033_seed_bank_income_profile"),
    ]

    operations = [
        migrations.AddField(
            model_name="credentialattribute",
            name="demo_value",
            field=models.CharField(blank=True, default="", max_length=500),
        ),
        migrations.RunPython(
            seed_bank_income_profile_demo_values,
            migrations.RunPython.noop,
        ),
    ]
