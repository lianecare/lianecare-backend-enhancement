# Generated by Django 3.1.5 on 2021-02-17 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='overview',
            field=models.TextField(blank=True),
        ),
    ]
