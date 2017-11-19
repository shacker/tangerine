# Generated by Django 2.1.dev20171104145028 on 2017-11-19 01:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tangerine', '0006_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='comment',
            name='website',
            field=models.URLField(blank=True),
        ),
        migrations.AlterField(
            model_name='comment',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tangerine.Comment', verbose_name='Parent comment'),
        ),
    ]
