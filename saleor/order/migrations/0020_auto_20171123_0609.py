# Generated by Django 1.11.5 on 2017-11-23 12:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("order", "0019_auto_20171109_1423")]

    operations = [migrations.RenameModel(old_name="OrderedItem", new_name="OrderLine")]
