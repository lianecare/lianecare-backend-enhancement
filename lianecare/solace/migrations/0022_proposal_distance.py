# Generated by Django 3.1.8 on 2021-05-06 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solace', '0021_auto_20210506_1928'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='distance',
            field=models.FloatField(blank=True, default=None, null=True),
        ),
    ]
