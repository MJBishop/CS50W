# Generated by Django 3.1.7 on 2023-12-28 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocklist', '0055_auto_20231220_1227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='name',
            field=models.CharField(max_length=20),
        ),
    ]