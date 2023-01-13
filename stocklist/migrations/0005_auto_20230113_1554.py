# Generated by Django 3.2.11 on 2023-01-13 15:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stocklist', '0004_auto_20230113_1252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='name',
            field=models.CharField(max_length=10),
        ),
        migrations.CreateModel(
            name='List',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('list_type', models.CharField(choices=[('AD', 'Addition'), ('CO', 'Count')], default='AD', max_length=2)),
                ('owner', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='lists', to=settings.AUTH_USER_MODEL)),
                ('session', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='lists', to='stocklist.session')),
            ],
        ),
    ]
