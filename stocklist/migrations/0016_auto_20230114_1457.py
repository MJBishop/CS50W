# Generated by Django 3.2.11 on 2023-01-14 14:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stocklist', '0015_auto_20230114_1456'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='item',
            name='unique name',
        ),
        migrations.AlterUniqueTogether(
            name='item',
            unique_together={('store', 'name')},
        ),
    ]