from django.db import migrations


def create_editor_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    editor_group, _ = Group.objects.get_or_create(name='Editor')
    perms = Permission.objects.filter(codename__in=['change_experience', 'change_project'])
    for perm in perms:
        editor_group.permissions.add(perm)


def remove_editor_group(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_experience_starred_by'),
    ]

    operations = [
        migrations.RunPython(create_editor_group, reverse_code=remove_editor_group),
    ]
