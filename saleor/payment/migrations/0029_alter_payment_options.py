# Generated by Django 3.2.2 on 2021-05-19 09:50

from django.core.management.sql import emit_post_migrate_signal
from django.db import migrations


def assing_permissions(apps, schema_editor):
    # force post signal as permissions are created in post migrate signals
    # related Django issue https://code.djangoproject.com/ticket/23422
    emit_post_migrate_signal(2, False, "default")
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    handle_payments = Permission.objects.filter(
        codename="handle_payments", content_type__app_label="payment"
    ).first()
    for group in Group.objects.iterator():
        group.permissions.add(handle_payments)


class Migration(migrations.Migration):

    dependencies = [
        ("payment", "0028_drop_searchable_key"),
        ("channel", "0003_alter_channel_default_country"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="payment",
            options={
                "ordering": ("pk",),
                "permissions": (("handle_payments", "Handle payments"),),
            },
        ),
        migrations.RunPython(assing_permissions, migrations.RunPython.noop),
    ]
