# Generated by Django 3.1.5 on 2021-01-22 13:10

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('processer', '0003_remove_video_firstframe'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='upload_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='video',
            name='upload_by',
            field=models.CharField(default='', max_length=150),
        ),
    ]