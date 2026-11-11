from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("portal_backend", "0038_usage_host_reporting_required"),
    ]

    operations = [
        migrations.AddField(
            model_name="usagereport",
            name="heartbeat_seconds",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
