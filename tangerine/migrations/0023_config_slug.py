# Generated by Django 2.0.1 on 2018-01-19 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tangerine', '0022_auto_20180115_2339'),
    ]

    operations = [
        migrations.AddField(
            model_name='config',
            name='slug',
            field=models.SlugField(default='blog', help_text='Must match a blog slug defined in top level urls.py. See docs.'),
        ),
    ]
