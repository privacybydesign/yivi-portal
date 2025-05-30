# Generated by Django 5.0.13 on 2025-05-16 11:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("portal_backend", "0003_remove_user_organization_user_organizations"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="relyingparty",
            name="approved_rp_details",
        ),
        migrations.RemoveField(
            model_name="relyingparty",
            name="published_rp_details",
        ),
        migrations.AddField(
            model_name="relyingparty",
            name="published",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="relyingparty",
            name="reviewed_rejected",
            field=models.BooleanField(default=False, null=True),
        ),
    ]
