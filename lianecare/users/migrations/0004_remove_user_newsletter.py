# Generated by Django 3.1.8 on 2021-05-09 15:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20210324_1627'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='newsletter',
        ),
    ]
