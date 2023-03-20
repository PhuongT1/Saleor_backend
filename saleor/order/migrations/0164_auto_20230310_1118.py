# Generated by Django 4.0.7 on 2022-09-26 10:15

from django.db import migrations, models


def rename_order_events(apps, _schema_editor):
    OrderEvent = apps.get_model("order", "OrderEvent")
    OrderEvent.objects.filter(type="transaction_void_requested").update(
        type="transaction_cancel_requested"
    )
    OrderEvent.objects.filter(type="transaction_capture_requested").update(
        type="transaction_charge_requested"
    )


class Migration(migrations.Migration):
    dependencies = [
        ("order", "0163_alter_orderevent_type"),
    ]
    operations = [
        migrations.RunPython(
            rename_order_events, reverse_code=migrations.RunPython.noop
        ),
        migrations.AlterField(
            model_name="order",
            name="charge_status",
            field=models.CharField(
                choices=[
                    ("none", "The order is not charged."),
                    ("partial", "The order is partially charged"),
                    ("full", "The order is fully charged"),
                    ("overcharged", "The order is overcharged"),
                ],
                db_index=True,
                default="none",
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="authorize_status",
            field=models.CharField(
                choices=[
                    ("none", "The funds are not authorized"),
                    (
                        "partial",
                        "The funds that are authorized and charged don't cover fully "
                        "the order's total",
                    ),
                    (
                        "full",
                        "The funds that are authorized and charged fully cover the "
                        "order's total",
                    ),
                ],
                db_index=True,
                default="none",
                max_length=32,
            ),
        ),
    ]
