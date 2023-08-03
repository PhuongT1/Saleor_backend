# Generated by Django 3.2.20 on 2023-07-25 15:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("attribute", "0036_assignedproductattributevalue_product_data_migration"),
    ]

    state_operations = [
        migrations.AlterField(
            model_name="assignedpageattributevalue",
            name="page",
            field=models.ForeignKey(
                db_index=False,
                null=False,
                blank=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="attributevalues",
                to="page.page",
            ),
        ),
        migrations.RemoveField(
            model_name="attributepage",
            name="assigned_pages",
        ),
        migrations.AlterUniqueTogether(
            name="assignedpageattributevalue",
            unique_together={("value", "page")},
        ),
        migrations.RemoveField(
            model_name="assignedpageattributevalue",
            name="assignment",
        ),
        migrations.DeleteModel(
            name="AssignedPageAttribute",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="assignedpageattributevalue",
            name="assignment",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="pagevalueassignment",
                to="attribute.AssignedPageAttribute",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="assignedpageattribute",
            name="page",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="attributes",
                to="page.Page",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="assignedpageattribute",
            name="assignment",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="pageassignments",
                to="attribute.AttributePage",
                null=True,
            ),
        ),
        # Remove FK constraints so that the DB doesn't try to truncate the references
        migrations.RunSQL(
            """
            ALTER TABLE attribute_assignedpageattribute
            DROP CONSTRAINT IF EXISTS
            attribute_assignedpa_assignment_id_db2b2662_fk_attribute;

            ALTER TABLE attribute_assignedpageattribute
            DROP CONSTRAINT IF EXISTS
            attribute_assignedpa_page_id_6db6dc92_fk_page_page;

            ALTER TABLE attribute_assignedpageattributevalue
            DROP CONSTRAINT IF EXISTS
            attribute_assignedpa_assignment_id_6863be0a_fk_attribute;

            ALTER TABLE attribute_assignedpageattributevalue
            DROP CONSTRAINT IF EXISTS
            attribute_assignedpageat_value_id_assignment_id_f51f07e4_uniq;
            """
        ),
        migrations.SeparateDatabaseAndState(state_operations=state_operations),
    ]