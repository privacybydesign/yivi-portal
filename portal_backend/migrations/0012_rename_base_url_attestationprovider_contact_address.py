# Generated by Django 5.0.13 on 2025-05-21 11:47

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("portal_backend", "0011_remove_relyingparty_reviewed_rejected_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="attestationprovider",
            old_name="base_url",
            new_name="contact_address",
        ),
    ]
