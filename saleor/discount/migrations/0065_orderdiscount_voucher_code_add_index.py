# Generated by Django 3.2.21 on 2023-10-04 10:26

from django.db import migrations
from django.contrib.postgres.operations import AddIndexConcurrently
from django.contrib.postgres.indexes import GinIndex


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("discount", "0064_orderdiscount_voucher_code"),
    ]

    operations = [
        AddIndexConcurrently(
            model_name="orderdiscount",
            index=GinIndex(
                fields=["voucher_code"], name="orderdiscount_voucher_code_idx"
            ),
        ),
    ]
