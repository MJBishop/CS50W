# Generated by Django 3.1.7 on 2021-03-07 12:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_auto_20210306_1856'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='user_name',
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(default='mike', on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='auctions.user', to_field='username'),
            preserve_default=False,
        ),
    ]