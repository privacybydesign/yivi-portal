from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("portal_backend", "0037_remove_organization_approved_logo"),
    ]

    operations = [
        migrations.AddField(
            model_name="usagereport",
            name="heartbeat_seconds",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
