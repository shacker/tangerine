# Generated by Django 2.0.1 on 2018-01-19 07:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tangerine', '0025_config_site_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='config',
            name='site_url',
        ),
    ]
