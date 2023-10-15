# Generated by Django 3.2.18 on 2023-04-06 11:43

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("order", "0168_order_bulk_permission"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="order",
            options={
                "ordering": ("-number",),
                "permissions": (
                    ("manage_orders", "Manage orders."),
                    ("manage_orders_import", "Manage orders import."),
                ),
            },
        ),
    ]
