# Generated by Django 3.1.13 on 2023-02-13 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0038_course_course_offer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='course_offer',
            field=models.CharField(blank=True, default='', max_length=250, null=True, verbose_name='offerta del corso'),
        ),
    ]
