# Generated by Django 1.10.3 on 2016-12-12 09:01
from __future__ import unicode_literals

import django.contrib.postgres.fields.hstore
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("product", "0021_add_hstore_extension")]

    operations = [
        migrations.RemoveField(model_name="product", name="attributes"),
        migrations.AddField(
            model_name="product",
            name="attributes",
            field=django.contrib.postgres.fields.hstore.HStoreField(
                default={}, verbose_name="attributes"
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="product_class",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="products",
                to="product.ProductClass",
            ),
        ),
    ]
