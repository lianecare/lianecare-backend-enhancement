# Generated by Django 3.1.8 on 2021-05-01 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_auto_20210501_1443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='amount_subtotal',
            field=models.IntegerField(default=0, verbose_name='Subtotale'),
        ),
        migrations.AlterField(
            model_name='order',
            name='amount_total',
            field=models.IntegerField(default=0, verbose_name='Totale'),
        ),
        migrations.AlterField(
            model_name='order',
            name='customer_stripe_id',
            field=models.CharField(default=None, max_length=255, null=True, verbose_name='STRIPE CUSTOMER ID'),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_intent_stripe_id',
            field=models.CharField(default=None, max_length=255, null=True, unique=True, verbose_name='STRIPE PAYMENT ID'),
        ),
        migrations.AlterField(
            model_name='order',
            name='price_stripe_id',
            field=models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='STRIPE PRICE ID'),
        ),
        migrations.AlterField(
            model_name='order',
            name='product_description',
            field=models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Descrizione'),
        ),
        migrations.AlterField(
            model_name='order',
            name='product_stripe_id',
            field=models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='STRIPE PRODUCT ID'),
        ),
        migrations.AlterField(
            model_name='order',
            name='session_stripe_id',
            field=models.CharField(default=None, max_length=255, null=True, unique=True, verbose_name='STRIPE SESSION ID'),
        ),
        migrations.AlterField(
            model_name='order',
            name='subscription_stripe_id',
            field=models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='STRIPE SUBSCRIPTION ID'),
        ),
    ]
