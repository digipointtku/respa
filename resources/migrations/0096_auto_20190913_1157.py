# Generated by Django 2.1.12 on 2019-09-13 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0095_auto_20190913_1151'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='state',
            field=models.CharField(choices=[('created', 'created'), ('cancelled', 'cancelled'), ('confirmed', 'confirmed'), ('denied', 'denied'), ('requested', 'requested'), ('waiting_for_payment', 'waiting for payment')], default='created', max_length=32, verbose_name='State'),
        ),
    ]
