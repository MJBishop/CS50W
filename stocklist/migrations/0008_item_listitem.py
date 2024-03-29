# Generated by Django 3.2.11 on 2023-01-14 08:35

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stocklist', '0007_alter_list_list_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
                ('store', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='stocklist.store')),
            ],
        ),
        migrations.CreateModel(
            name='ListItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=7, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1000000)])),
                ('item', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='item', to='stocklist.item')),
                ('list', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='list_items', to='stocklist.list')),
            ],
        ),
    ]
