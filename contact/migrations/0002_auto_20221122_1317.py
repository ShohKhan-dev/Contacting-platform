# Generated by Django 3.1.5 on 2022-11-22 10:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='telegram_id',
            new_name='username',
        ),
    ]
