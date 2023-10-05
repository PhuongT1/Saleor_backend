# Generated by Django 3.2.21 on 2023-09-26 08:44

import django.contrib.postgres.indexes
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("discount", "0052_move_codes_to_new_model"),
    ]

    operations = [
        migrations.AddField(
            model_name="vouchercustomer",
            name="voucher_code",
            field=models.ForeignKey(
                db_index=False,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="customers",
                to="discount.vouchercode",
            ),
        ),
    ]
