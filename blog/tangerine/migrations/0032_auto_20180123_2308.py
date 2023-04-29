# Generated by Django 2.0.1 on 2018-01-24 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tangerine', '0031_auto_20180122_2345'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Config',
            new_name='Blog',
        ),
        migrations.AlterModelOptions(
            name='blog',
            options={'verbose_name_plural': 'Blogs'},
        ),
        migrations.AlterField(
            model_name='post',
            name='enable_comments',
            field=models.BooleanField(default=True, help_text='Disable to turn off comments for this Post/Page only.            Overriden if Global Comment Enable is off in Blog config.'),
        ),
    ]