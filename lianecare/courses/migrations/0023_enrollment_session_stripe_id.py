# Generated by Django 3.1.7 on 2021-04-06 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0022_auto_20210406_1804'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrollment',
            name='session_stripe_id',
            field=models.CharField(blank=True, default=None, max_length=255, null=True, unique=True),
        ),
    ]
