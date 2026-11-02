# Migration to remove discussion field from UserReputationLog

from django.db import migrations


def drop_discussion_column(apps, schema_editor):
    """Удаляет столбец discussion_id, если он существует.

    Историческая миграция использовала PostgreSQL-синтаксис
    ``DROP COLUMN IF EXISTS``, который не поддерживается SQLite.
    """
    connection = schema_editor.connection
    table_name = 'users_userreputationlog'

    with connection.cursor() as cursor:
        table_names = connection.introspection.table_names(cursor)
        if table_name not in table_names:
            return
        columns = {
            column.name
            for column in connection.introspection.get_table_description(cursor, table_name)
        }
        if 'discussion_id' in columns:
            cursor.execute(f'ALTER TABLE "{table_name}" DROP COLUMN "discussion_id";')


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_add_banner_customization'),
    ]

    operations = [
        migrations.RunPython(drop_discussion_column, migrations.RunPython.noop),
    ]
