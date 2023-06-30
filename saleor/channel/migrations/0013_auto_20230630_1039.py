# Generated by Django 3.2.19 on 2023-06-30 10:39

import django.contrib.postgres.indexes
from django.db import migrations, models
import saleor.core.utils.json_serializer


class Migration(migrations.Migration):

    dependencies = [
        ('channel', '0012_channel_delete_expired_orders_after'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='metadata',
            field=models.JSONField(blank=True, default=dict, encoder=saleor.core.utils.json_serializer.CustomJsonEncoder, null=True),
        ),
        migrations.AddField(
            model_name='channel',
            name='private_metadata',
            field=models.JSONField(blank=True, default=dict, encoder=saleor.core.utils.json_serializer.CustomJsonEncoder, null=True),
        ),
        migrations.AddIndex(
            model_name='channel',
            index=django.contrib.postgres.indexes.GinIndex(fields=['private_metadata'], name='channel_p_meta_idx'),
        ),
        migrations.AddIndex(
            model_name='channel',
            index=django.contrib.postgres.indexes.GinIndex(fields=['metadata'], name='channel_meta_idx'),
        ),
    ]
