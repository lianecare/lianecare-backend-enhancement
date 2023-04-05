# Generated by Django 3.1.8 on 2021-05-08 05:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solace', '0024_auto_20210507_1313'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobpost',
            name='status',
            field=models.CharField(choices=[(None, ''), ('NO_SHOW', 'Non visibile'), ('ACTIVE', 'Pubblicato'), ('DELETE', 'Non voglio dirlo'), ('KO_DONT_NEED', 'Non ne ho più bisogno'), ('KO_OTHER_PLATFORM', 'Ho trovato un Caregiver con altre piattaforme'), ('KO_OTHER', 'Ho trovato il Caregiver in altro modo'), ('OK_SOLACE', 'Ho trovato il Caregiver con LianeCare')], default='ACTIVE', max_length=55),
        ),
    ]
