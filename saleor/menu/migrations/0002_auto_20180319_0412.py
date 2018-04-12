# Generated by Django 2.0.3 on 2018-03-19 09:12

from django.db import migrations


def create_default_menus(apps, schema_editor):
    # slugs for menus created by default
    DEFAULT_MENUS = ['navbar', 'footer']

    Menu = apps.get_model('menu', 'Menu')
    for slug in DEFAULT_MENUS:
        Menu.objects.get_or_create(slug=slug)


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_menus, migrations.RunPython.noop)
    ]
