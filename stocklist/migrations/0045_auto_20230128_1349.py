# Generated by Django 3.2.11 on 2023-01-28 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocklist', '0044_auto_20230128_1341'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='origin',
        ),
        migrations.AlterField(
            model_name='store',
            name='name',
            field=models.CharField(default='Store', max_length=20),
        ),
    ]