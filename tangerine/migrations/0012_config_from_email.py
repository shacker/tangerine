# Generated by Django 2.1.dev20171104145028 on 2017-12-04 07:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tangerine', '0011_akismet'),
    ]

    operations = [
        migrations.AddField(
            model_name='config',
            name='from_email',
            field=models.CharField(default='June Carter-Cash <june@example.com>', help_text='Emails sent FROM tangerine, such as comment moderation messages, will originate from this address.            Should be a real, reachable email.', max_length=100),
        ),
    ]
