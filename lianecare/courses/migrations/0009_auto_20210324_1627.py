# Generated by Django 3.1.7 on 2021-03-24 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0008_course_available'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='price',
            field=models.IntegerField(default=0, help_text='Prezzo in centesimi', verbose_name='Prezzo'),
        ),
    ]