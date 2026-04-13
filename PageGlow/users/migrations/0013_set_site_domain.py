from django.db import migrations
from django.conf import settings


def set_site_domain(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    Site.objects.update_or_create(
        id=settings.SITE_ID,
        defaults={
            'domain': settings.SITE_DOMAIN,
            'name': 'Flachub'
        }
    )


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.RunPython(set_site_domain, migrations.RunPython.noop),
    ]
