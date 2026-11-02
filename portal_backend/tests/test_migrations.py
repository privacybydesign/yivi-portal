from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase

BEFORE = [("portal_backend", "0036_usage_reporting")]
AFTER = [("portal_backend", "0037_remove_organization_approved_logo")]


def organization_columns() -> set[str]:
    with connection.cursor() as cursor:
        return {
            column.name
            for column in connection.introspection.get_table_description(
                cursor, "portal_backend_organization"
            )
        }


class RemoveApprovedLogoMigrationTest(TransactionTestCase):
    """0030 removed approved_logo until #224 rewrote it without that step.

    Databases migrated in between lost the column; every other database still
    has it. 0037 has to leave both kinds without the column, and must not fail
    on the ones where it is already gone.
    """

    def migrate(self, targets):
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(targets)

    def tearDown(self):
        self.migrate(executor_leaf_nodes())

    def test_drops_the_column_where_it_still_exists(self):
        self.migrate(BEFORE)
        self.assertIn("approved_logo", organization_columns())
        self.migrate(AFTER)
        self.assertNotIn("approved_logo", organization_columns())

    def test_passes_where_the_original_0030_already_dropped_it(self):
        self.migrate(BEFORE)
        with connection.schema_editor() as editor:
            executor = MigrationExecutor(connection)
            organization = executor.loader.project_state(BEFORE).apps.get_model(
                "portal_backend", "Organization"
            )
            editor.remove_field(
                organization, organization._meta.get_field("approved_logo")
            )
        self.assertNotIn("approved_logo", organization_columns())
        self.migrate(AFTER)
        self.assertNotIn("approved_logo", organization_columns())

    def test_reverting_restores_the_column(self):
        self.migrate(AFTER)
        self.assertNotIn("approved_logo", organization_columns())
        self.migrate(BEFORE)
        self.assertIn("approved_logo", organization_columns())


def executor_leaf_nodes():
    return MigrationExecutor(connection).loader.graph.leaf_nodes()
