# Generated by Django 5.0.13 on 2025-06-04 09:40

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("portal_backend", "0017_merge_20250604_0915"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="organization",
            name="registration_number",
        ),
    ]
