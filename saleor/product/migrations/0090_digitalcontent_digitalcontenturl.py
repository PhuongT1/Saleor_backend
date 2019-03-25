# Generated by Django 2.1.7 on 2019-03-25 13:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0089_auto_20190225_0252'),
    ]

    operations = [
        migrations.CreateModel(
            name='DigitalContent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content_type', models.CharField(choices=[('file', 'digital_product')], default='file', max_length=128)),
                ('content_file', models.FileField(blank=True, upload_to='digital_contents')),
                ('max_downloads', models.IntegerField(blank=True, null=True)),
                ('url_valid_days', models.IntegerField(blank=True, null=True)),
                ('product_variant', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='digital_content', to='product.ProductVariant')),
            ],
        ),
        migrations.CreateModel(
            name='DigitalContentUrl',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.UUIDField(editable=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('download_num', models.IntegerField(default=0)),
                ('content', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='urls', to='product.DigitalContent')),
            ],
        ),
    ]
