from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("portal_backend", "0032_alter_credentialattribute_unique_together"),
    ]

    operations = [
        migrations.AddField(
            model_name="credentialattribute",
            name="demo_value",
            field=models.CharField(blank=True, default="", max_length=500),
        ),
    ]
