# Generated by Django 3.2.11 on 2023-01-28 10:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stocklist', '0041_auto_20230128_1021'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stocklist',
            old_name='count',
            new_name='stocktake',
        ),
    ]