# Generated by Django 3.1.8 on 2021-06-26 16:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('solace', '0028_auto_20210626_1520'),
    ]

    operations = [
        migrations.RenameField(
            model_name='caregiverpromore',
            old_name='notify_new_jobpost',
            new_name='notify_new_proposal',
        ),
        migrations.RenameField(
            model_name='personmore',
            old_name='notify_new_jobpost',
            new_name='notify_new_proposal',
        ),
    ]
