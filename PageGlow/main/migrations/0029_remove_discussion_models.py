# Generated migration to remove Discussion and DiscussionComment models

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0028_alter_notification_notification_type'),
    ]

    operations = [
        # Удаление таблиц Discussion и DiscussionComment
        migrations.RunSQL(
            sql=[
                "DROP TABLE IF EXISTS main_discussioncomment_likes CASCADE;",
                "DROP TABLE IF EXISTS main_discussion_tags CASCADE;",
                "DROP TABLE IF EXISTS main_discussion_favorites CASCADE;",
                "DROP TABLE IF EXISTS main_discussion_likes CASCADE;",
                "DROP TABLE IF EXISTS main_discussioncomment CASCADE;",
                "DROP TABLE IF EXISTS main_discussion CASCADE;",
                "DROP TABLE IF EXISTS main_discussioncategory CASCADE;",
            ],
            reverse_sql=[],  # No rollback possible
        ),
    ]
