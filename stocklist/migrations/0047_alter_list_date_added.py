# Generated by Django 3.2.11 on 2023-01-28 15:07

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('stocklist', '0046_auto_20230128_1356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='list',
            name='date_added',
            field=models.DateTimeField(default=django.utils.timezone.localdate, help_text='The date tems were added/removed from the Store'),
        ),
    ]