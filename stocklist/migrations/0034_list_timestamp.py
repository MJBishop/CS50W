# Generated by Django 3.2.11 on 2023-01-27 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocklist', '0033_auto_20230127_0837'),
    ]

    operations = [
        migrations.AddField(
            model_name='list',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, default=None),
            preserve_default=False,
        ),
    ]
