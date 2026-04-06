# Migration to remove discussion field from UserReputationLog

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_add_banner_customization'),
    ]

    operations = [
        # Удаление столбца discussion из таблицы репутации
        migrations.RunSQL(
            sql=[
                "ALTER TABLE users_userreputationlog DROP COLUMN IF EXISTS discussion_id;",
            ],
            reverse_sql=[],  # No rollback possible
        ),
    ]
