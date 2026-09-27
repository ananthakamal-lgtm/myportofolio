from django.db import migrations


def promote_to_superuser(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    users = User.objects.filter(username__iexact='anantha.kamal')
    for u in users:
        u.is_staff = True
        u.is_superuser = True
        u.save()


def reverse_promote(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_project_starred_by'),
    ]

    operations = [
        migrations.RunPython(promote_to_superuser, reverse_code=reverse_promote),
    ]
