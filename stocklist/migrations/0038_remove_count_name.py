# Generated by Django 3.2.11 on 2023-01-27 13:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stocklist', '0037_count_frequency'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='count',
            name='name',
        ),
    ]
