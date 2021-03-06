# Generated by Django 2.1.dev20171104145028 on 2017-11-19 00:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tangerine', '0004_auto_20171117_0728'),
    ]

    operations = [
        migrations.AddField(
            model_name='config',
            name='comment_system',
            field=models.CharField(choices=[('native', 'Native')], default='native', help_text='Select the commenting system to be used. Tangerine\'s is "Native".', max_length=12),
        ),
        migrations.AddField(
            model_name='config',
            name='enable_comments_global',
            field=models.BooleanField(default=True, help_text='Disable to turn off comments site-wide.            With global comments enabled, you can still disable comments per-post.)'),
        ),
        migrations.AddField(
            model_name='post',
            name='enable_comments',
            field=models.BooleanField(default=True, help_text='Disable to turn off comments for this Post/Page only.            Overriden if Global Comment Enable is off in Config.'),
        ),
    ]
