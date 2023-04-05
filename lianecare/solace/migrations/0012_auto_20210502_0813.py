# Generated by Django 3.1.8 on 2021-05-02 08:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('solace', '0011_auto_20210502_0712'),
    ]

    operations = [
        migrations.AlterField(
            model_name='caregiverpromore',
            name='has_basic_course',
            field=models.BooleanField(default=False, verbose_name='Corso base'),
        ),
        migrations.AlterField(
            model_name='caregiverpromore',
            name='has_pro_course',
            field=models.BooleanField(default=False, verbose_name='Corso PRO'),
        ),
        migrations.AlterField(
            model_name='familymember',
            name='user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='family_members', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='personmore',
            name='has_basic_course',
            field=models.BooleanField(default=False, verbose_name='Corso base'),
        ),
        migrations.AlterField(
            model_name='personmore',
            name='has_pro_course',
            field=models.BooleanField(default=False, verbose_name='Corso PRO'),
        ),
    ]