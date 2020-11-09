# Generated by Django 3.1 on 2020-11-02 11:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    # TODO squash before merging multicurrency into master
    dependencies = [
        ("channel", "0003_auto_20201015_1107"),
        ("product", "0138_auto_20201102_0935"),
    ]

    operations = [
        migrations.AlterField(
            model_name="productvariantchannellisting",
            name="channel",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="variant_listings",
                to="channel.channel",
            ),
        ),
        migrations.AlterField(
            model_name="productvariantchannellisting",
            name="variant",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="channel_listings",
                to="product.productvariant",
            ),
        ),
    ]
