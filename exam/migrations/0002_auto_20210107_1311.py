# Generated by Django 3.0.8 on 2021-01-07 07:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player_scores',
            name='start_datetime',
            field=models.DateTimeField(default=datetime.datetime(2021, 1, 7, 13, 11, 56, 35195)),
        ),
    ]
