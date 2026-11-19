"""Custom migration operations shared by GovReady-Q apps."""

from django.db import migrations


class RenameIndexOrCreate(migrations.RenameIndex):
    """Rename an unnamed ``index_together`` index to a named ``Meta.indexes`` index.

    Behaves like ``RenameIndex(old_fields=...)``, except that if the old unnamed
    index is missing from the database, the new index is created instead of
    raising ``ValueError``.

    The old index can be missing on SQLite. Django 5.1+ no longer recreates
    ``index_together`` indexes when an earlier migration rebuilds the table there,
    so those indexes may already have been dropped. PostgreSQL and MySQL keep the
    index, and a plain rename happens.
    """

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        model = to_state.apps.get_model(app_label, self.model_name)
        if not self.allow_migrate_model(schema_editor.connection.alias, model):
            return
        if self.old_fields:
            columns = [model._meta.get_field(field).column for field in self.old_fields]
            matching = schema_editor._constraint_names(
                from_state.apps.get_model(app_label, self.model_name),
                column_names=columns,
                index=True,
            )
            if not matching:
                new_index = to_state.models[app_label, self.model_name_lower].get_index_by_name(self.new_name)
                schema_editor.add_index(model, new_index)
                return
        super().database_forwards(app_label, schema_editor, from_state, to_state)
