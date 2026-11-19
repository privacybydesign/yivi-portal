import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portal_backend", "0039_usagereport_heartbeat_seconds"),
    ]

    operations = [
        # Where users of the Yivi app reach the organization's support. Apart
        # from contact_email, which is how Yivi reaches the organization and
        # stays private. Optional: organizations imported from the scheme
        # repositories mostly have neither.
        migrations.AddField(
            model_name="organization",
            name="support_email",
            field=models.EmailField(
                blank=True,
                help_text="Where users of the Yivi app can ask this organization for help. Public: the Yivi app shows it once it is published in the scheme.",
                max_length=255,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="organization",
            name="support_url",
            field=models.URLField(
                blank=True,
                help_text="The organization's support page for users of the Yivi app. Public: the Yivi app shows it once it is published in the scheme.",
                max_length=255,
                null=True,
                validators=[
                    django.core.validators.URLValidator(
                        message="Enter a valid URL that starts with https://.",
                        schemes=["https"],
                    )
                ],
            ),
        ),
    ]
