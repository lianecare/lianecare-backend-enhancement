# Generated by Django 3.1.8 on 2021-05-02 05:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('solace', '0009_auto_20210501_2000'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='company',
            options={'ordering': ('name',), 'verbose_name': 'Azienda', 'verbose_name_plural': 'Aziende'},
        ),
    ]
