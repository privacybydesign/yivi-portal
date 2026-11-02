from django.db import migrations

# 0030 removed Organization.approved_logo when #214 added it, until #224
# rewrote 0030 without that step. A database that applied 0030 in between has
# no such column any more; every other database still has it, and the model
# has not had the field since #214. So the field always leaves the migration
# state, but the column is only dropped where it still exists: a plain
# RemoveField would fail on the databases where it is already gone.

TABLE_COLUMN = "approved_logo"


def _has_column(schema_editor, model) -> bool:
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        columns = connection.introspection.get_table_description(
            cursor, model._meta.db_table
        )
    return any(column.name == TABLE_COLUMN for column in columns)


def drop_column_if_present(apps, schema_editor):
    organization = apps.get_model("portal_backend", "Organization")
    if _has_column(schema_editor, organization):
        schema_editor.remove_field(
            organization, organization._meta.get_field("approved_logo")
        )


def restore_column_if_absent(apps, schema_editor):
    organization = apps.get_model("portal_backend", "Organization")
    if not _has_column(schema_editor, organization):
        schema_editor.add_field(
            organization, organization._meta.get_field("approved_logo")
        )


class Migration(migrations.Migration):
    dependencies = [
        ("portal_backend", "0036_usage_reporting"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(drop_column_if_present, restore_column_if_absent),
            ],
            state_operations=[
                migrations.RemoveField(model_name="organization", name="approved_logo"),
            ],
        ),
    ]
