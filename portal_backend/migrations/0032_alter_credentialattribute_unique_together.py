from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portal_backend", "0031_credentialattribute_optional"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="credentialattribute",
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name="credentialattribute",
            constraint=models.UniqueConstraint(
                fields=["credential", "name_en"],
                name="unique_credentialattribute_credential_name_en",
            ),
        ),
    ]
