# Generated by Django 3.1.8 on 2021-06-27 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solace', '0032_auto_20210627_1822'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='service',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='service',
            constraint=models.UniqueConstraint(fields=('caregiver', 'category'), name='unique_category_for_caregiver'),
        ),
    ]