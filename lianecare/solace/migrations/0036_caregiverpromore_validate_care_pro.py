# Generated by Django 3.1.13 on 2023-01-18 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solace', '0035_auto_20220317_1223'),
    ]

    operations = [
        migrations.AddField(
            model_name='caregiverpromore',
            name='validate_care_pro',
            field=models.BooleanField(blank=True, default=None, null=True, verbose_name='Validate'),
        ),
    ]
