# Generated migration to remove Discussion and DiscussionComment models

from django.db import migrations

DISCUSSION_TABLES = [
    'main_discussioncomment_likes',
    'main_discussion_tags',
    'main_discussion_favorites',
    'main_discussion_likes',
    'main_discussioncomment',
    'main_discussion',
    'main_discussioncategory',
]


def drop_discussion_tables(apps, schema_editor):
    """Удаляет таблицы обсуждений, если они существуют.

    PostgreSQL требует CASCADE для таблиц со связями, SQLite не поддерживает
    этот синтаксис. Поэтому SQL зависит от используемой СУБД.
    """
    connection = schema_editor.connection
    existing_tables = set(connection.introspection.table_names())

    with connection.cursor() as cursor:
        for table in DISCUSSION_TABLES:
            if table not in existing_tables:
                continue
            if connection.vendor == 'postgresql':
                cursor.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE;')
            else:
                cursor.execute(f'DROP TABLE IF EXISTS "{table}";')


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0028_alter_notification_notification_type'),
    ]

    operations = [
        migrations.RunPython(drop_discussion_tables, migrations.RunPython.noop),
    ]
