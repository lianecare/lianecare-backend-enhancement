# Generated by Django 3.1.8 on 2021-04-18 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0030_auto_20210409_0953'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='type',
            field=models.CharField(choices=[('BASIC', 'Base'), ('PRO', 'Avanzato')], default='BASIC', max_length=25, verbose_name='Tipo corso'),
        ),
    ]
