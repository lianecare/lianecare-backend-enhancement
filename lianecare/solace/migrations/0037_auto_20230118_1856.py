# Generated by Django 3.1.13 on 2023-01-18 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solace', '0036_caregiverpromore_validate_care_pro'),
    ]

    operations = [
        migrations.AlterField(
            model_name='caregiverpromore',
            name='validate_care_pro',
            field=models.BooleanField(blank=True, default=False, null=True, verbose_name='Validate'),
        ),
    ]
