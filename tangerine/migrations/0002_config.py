# Generated by Django 2.1.dev20171104145028 on 2017-11-16 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tangerine', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='To be displayed in page header and as part of HTML title tag', max_length=140)),
                ('num_posts_per_list_view', models.SmallIntegerField(default=10, help_text='Used on default homepage, categories, date archives, etc.)', verbose_name='Number of Posts Per List View')),
                ('google_analytics_id', models.CharField(blank=True, help_text='Enter just the GA tracking ID provided by Google, not the entire codeblock, e.g UA-123456-2.', max_length=16)),
            ],
        ),
    ]
