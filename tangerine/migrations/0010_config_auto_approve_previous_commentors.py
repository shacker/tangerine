# Generated by Django 2.1.dev20171104145028 on 2017-11-23 22:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tangerine', '0009_approvedcommentor'),
    ]

    operations = [
        migrations.AddField(
            model_name='config',
            name='auto_approve_previous_commentors',
            field=models.BooleanField(default=True, help_text='Comments with emails that have been approved before and that pass spam checks            will be posted immediately.'),
        ),
    ]
