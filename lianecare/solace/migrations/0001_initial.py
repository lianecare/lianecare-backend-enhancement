from django.contrib.postgres.operations import HStoreExtension, CryptoExtension
from django.db import migrations


class Migration(migrations.Migration):
    initial = True

    operations = [
        HStoreExtension(),
        CryptoExtension(),
    ]
