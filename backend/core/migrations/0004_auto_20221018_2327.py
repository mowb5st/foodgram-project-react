# Generated by Django 2.2.16 on 2022-10-18 17:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20221018_2315'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingredient',
            old_name='title',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='tag',
            old_name='title',
            new_name='name',
        ),
    ]
