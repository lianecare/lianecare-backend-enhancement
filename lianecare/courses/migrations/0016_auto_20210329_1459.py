# Generated by Django 3.1.7 on 2021-03-29 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0015_auto_20210329_1414'),
    ]

    operations = [
        migrations.AlterField(
            model_name='module',
            name='duration',
            field=models.PositiveIntegerField(default=1, verbose_name='Durata in secondi'),
        ),
    ]