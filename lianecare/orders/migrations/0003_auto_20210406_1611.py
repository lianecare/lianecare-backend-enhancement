# Generated by Django 3.1.7 on 2021-04-06 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_auto_20210405_1702'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='amount_subtotal',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='order',
            name='customer_stripe_id',
            field=models.CharField(default=None, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_intent_stripe_id',
            field=models.CharField(default=None, max_length=255, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='price_stripe_id',
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='product_stripe_id',
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='session_stripe_id',
            field=models.CharField(default=None, max_length=255, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='subscription_stripe_id',
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
    ]
