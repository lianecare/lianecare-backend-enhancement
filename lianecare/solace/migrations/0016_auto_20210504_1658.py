# Generated by Django 3.1.8 on 2021-05-04 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solace', '0015_auto_20210504_1503'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobpost',
            name='experience',
            field=models.IntegerField(choices=[(None, 'Seleziona'), (0, 'Indifferente'), (3, '+3 anni'), (5, '+5 anni'), (10, '+10 anni')], verbose_name='Anni di esperienza'),
        ),
        migrations.AlterField(
            model_name='jobpost',
            name='when',
            field=models.IntegerField(choices=[(None, 'Seleziona'), (0, 'Indifferente'), (1, 'Il prima possibile'), (7, 'Entro una settimana'), (30, 'Entro un mese')]),
        ),
    ]
