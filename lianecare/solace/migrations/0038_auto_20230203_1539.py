# Generated by Django 3.1.13 on 2023-02-03 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solace', '0037_auto_20230118_1856'),
    ]

    operations = [
        migrations.AlterField(
            model_name='caregiverpromore',
            name='how_know_us',
            field=models.CharField(blank=True, choices=[(None, ''), ('GOOGLE', 'Google'), ('YOUTUBE', 'Youtube'), ('FORUM', 'Gruppi o Forum'), ('FACEBOOK', 'Facebook'), ('LINKEDIN', 'Linkedin'), ('BANNER', 'Banner Ads'), ('FRIENDS', 'Amici e Famiglia'), ('PRESS', 'Press: News, Magazine, Blog'), ('FLYER', 'volantino'), ('OTHER', 'Altro')], max_length=35),
        ),
        migrations.AlterField(
            model_name='personmore',
            name='how_know_us',
            field=models.CharField(blank=True, choices=[(None, ''), ('GOOGLE', 'Google'), ('YOUTUBE', 'Youtube'), ('FORUM', 'Gruppi o Forum'), ('FACEBOOK', 'Facebook'), ('LINKEDIN', 'Linkedin'), ('BANNER', 'Banner Ads'), ('FRIENDS', 'Amici e Famiglia'), ('PRESS', 'Press: News, Magazine, Blog'), ('FLYER', 'volantino'), ('OTHER', 'Altro')], max_length=35),
        ),
    ]