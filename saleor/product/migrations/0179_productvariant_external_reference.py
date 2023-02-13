# Generated by Django 3.2.16 on 2022-12-02 12:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("product", "0178_product_external_reference"),
    ]

    operations = [
        migrations.AddField(
            model_name="productvariant",
            name="external_reference",
            field=models.CharField(
                blank=True, db_index=True, max_length=250, null=True, unique=True
            ),
        ),
    ]
