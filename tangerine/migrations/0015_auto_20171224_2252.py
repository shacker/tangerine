# Generated by Django 2.0 on 2017-12-25 06:52

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tangerine', '0014_auto_20171217_0041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='pub_date',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, verbose_name='Publication Date/Time'),
            preserve_default=False,
        ),
    ]
