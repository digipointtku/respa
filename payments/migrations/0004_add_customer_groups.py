# Generated by Django 2.2.24 on 2021-10-19 09:01

from decimal import Decimal
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0003_add_product_sap_unit'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerGroup',
            fields=[
                ('id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('name_fi', models.CharField(max_length=200, null=True, verbose_name='Name')),
                ('name_en', models.CharField(max_length=200, null=True, verbose_name='Name')),
                ('name_sv', models.CharField(max_length=200, null=True, verbose_name='Name')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductCustomerGroup',
            fields=[
                ('id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('name_fi', models.CharField(max_length=200, null=True, verbose_name='Name')),
                ('name_en', models.CharField(max_length=200, null=True, verbose_name='Name')),
                ('name_sv', models.CharField(max_length=200, null=True, verbose_name='Name')),
                ('price', models.DecimalField(decimal_places=2, help_text='This will override product price field.', max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='price including VAT')),
                ('customer_group', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, related_name='customer_group', to='payments.CustomerGroup', verbose_name='Customer group')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='product_customer_groups', to='payments.Product', verbose_name='Product')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
