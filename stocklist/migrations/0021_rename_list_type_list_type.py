# Generated by Django 3.2.11 on 2023-01-21 08:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stocklist', '0020_auto_20230120_1019'),
    ]

    operations = [
        migrations.RenameField(
            model_name='list',
            old_name='list_type',
            new_name='type',
        ),
    ]
