# Generated by Django 3.0.5 on 2020-04-16 06:07

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("account", "0043_rename_service_account_to_app"),
        ("webhook", "0003_unmount_service_account"),
    ]

    state_operations = [
        migrations.RemoveField(
            model_name="apptoken",
            name="app",
        ),
        migrations.DeleteModel(
            name="App",
        ),
        migrations.DeleteModel(
            name="AppToken",
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(state_operations=state_operations)
    ]
