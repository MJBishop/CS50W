# Generated by Django 3.2.11 on 2023-01-28 09:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stocklist', '0039_rename_countlist_stocklist'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockPeriod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('frequency', models.CharField(choices=[('MO', 'Monthly'), ('WE', 'Weekly'), ('DA', 'Daily')], default='DA', editable=False, max_length=2)),
                ('store', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='stock_periods', to='stocklist.store')),
            ],
        ),
    ]