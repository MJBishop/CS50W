# Generated by Django 3.1.7 on 2021-03-13 14:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_auto_20210311_1054'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='owner',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='listings', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='listing',
            name='title',
            field=models.CharField(max_length=100),
        ),
    ]