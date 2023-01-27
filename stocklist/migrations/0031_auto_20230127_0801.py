# Generated by Django 3.2.11 on 2023-01-27 08:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stocklist', '0030_auto_20230127_0732'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='store',
            name='unique name owner',
        ),
        migrations.RenameField(
            model_name='store',
            old_name='owner',
            new_name='user',
        ),
        migrations.AddField(
            model_name='sessionlist',
            name='user',
            field=models.ForeignKey(default=None, editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='session_lists', to='stocklist.user'),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name='store',
            constraint=models.UniqueConstraint(fields=('user', 'name'), name='unique name user'),
        ),
    ]
