from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portal_backend", "0034_user_public_id"),
    ]

    operations = [
        # Registration requires an email address and a phone number, but the
        # column stays nullable: organizations imported from the scheme
        # repositories carry neither, so the requirement is enforced by
        # OrganizationSerializer rather than by the database.
        migrations.AddField(
            model_name="organization",
            name="contact_email",
            field=models.EmailField(blank=True, max_length=255, null=True),
        ),
    ]
