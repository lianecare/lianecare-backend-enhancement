# Generated by Django 3.1.7 on 2021-03-29 14:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('djstripe', '0007_2_4'),
        ('courses', '0014_remove_course_id_product_stipe'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='enrollment',
            name='payment',
        ),
        migrations.AddField(
            model_name='enrollment',
            name='charge_stripe',
            field=models.OneToOneField(blank=True, help_text="ID del pagamento in Stripe se c'è stata una vendita", null=True, on_delete=django.db.models.deletion.SET_NULL, to='djstripe.charge'),
        ),
        migrations.AlterField(
            model_name='course',
            name='product_stripe',
            field=models.OneToOneField(blank=True, help_text='ID prodotto in Stripe', null=True, on_delete=django.db.models.deletion.SET_NULL, to='djstripe.product'),
        ),
    ]
