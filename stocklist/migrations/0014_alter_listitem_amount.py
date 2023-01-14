# Generated by Django 3.2.11 on 2023-01-14 14:29

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocklist', '0013_alter_listitem_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listitem',
            name='amount',
            field=models.DecimalField(decimal_places=1, max_digits=7, validators=[django.core.validators.MinValueValidator(Decimal('0')), django.core.validators.MaxValueValidator(Decimal('1000000'))]),
        ),
    ]
