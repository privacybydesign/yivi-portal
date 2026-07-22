import uuid

from django.db import migrations, models


def generate_public_ids(apps, schema_editor):
    """Assign a unique UUID to every existing user."""
    User = apps.get_model("portal_backend", "User")
    for user in User.objects.all():
        user.public_id = uuid.uuid4()
        user.save(update_fields=["public_id"])


class Migration(migrations.Migration):

    dependencies = [
        ("portal_backend", "0033_credentialattribute_demo_value"),
    ]

    operations = [
        # 1. Add the column without the unique constraint so existing rows are
        #    allowed to share the (single, schema-level) default value.
        migrations.AddField(
            model_name="user",
            name="public_id",
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True),
        ),
        # 2. Backfill a distinct UUID per existing row.
        migrations.RunPython(generate_public_ids, migrations.RunPython.noop),
        # 3. Enforce uniqueness now that every row has its own value.
        migrations.AlterField(
            model_name="user",
            name="public_id",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
