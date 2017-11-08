# Generated by Django 2.1.dev20171104145028 on 2017-11-08 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tangerine', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='ptype',
            field=models.CharField(choices=[('post', 'Post'), ('page', 'Page')], default='post', help_text='Select Page for semi-static pages. See docs for info.', max_length=6),
        ),
    ]
