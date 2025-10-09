from django.db.migrations import CreateModel

from django.db import connection


def check_table_name_exists(db_table):
    """Проверка, что таблица с указанным названием существует в бд

    :param db_table: Название проверяемой таблицы
    :type db_table: str

    :return: Существует ли таблица с указанным названием в бд
    :rtype: bool
    """
    return db_table in connection.introspection.table_names()


class CreateModelIfNotExist(CreateModel):
    """Операция создания таблицы в бд, только если она не существует."""

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        model = to_state.apps.get_model(app_label, self.name)
        db_table = self.options.get('db_table', model._meta.db_table)

        if not check_table_name_exists(db_table):
            super().database_forwards(
                app_label, schema_editor, from_state, to_state)
