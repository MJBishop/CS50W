# Generated by Django 3.2.11 on 2023-01-25 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocklist', '0025_auto_20230124_1314'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='department',
        ),
        migrations.AlterField(
            model_name='item',
            name='name',
            field=models.CharField(max_length=80),
        ),
    ]
