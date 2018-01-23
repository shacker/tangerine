# Generated by Django 2.0.1 on 2018-01-22 07:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tangerine', '0026_remove_config_site_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='blog',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tangerine.Config'),
        ),
        migrations.AlterField(
            model_name='config',
            name='slug',
            field=models.SlugField(default='blog', help_text='Must match a blog slug defined in top level urls.py (without slashes). See docs.'),
        ),
    ]
