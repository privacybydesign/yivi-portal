# Generated by Django 5.0.13 on 2025-06-02 15:02


from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("portal_backend", "0014_attestationprovider_ap_slug"),
    ]

    operations = [
        migrations.RenameField(
            model_name="yivitrustmodelenv",
            old_name="contact",
            new_name="contact_website",
        ),
    ]
