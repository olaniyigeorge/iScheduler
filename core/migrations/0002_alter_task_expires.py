# Generated by Django 5.1.3 on 2024-11-22 13:59

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='expires',
            field=models.DateTimeField(default=datetime.datetime(2024, 11, 22, 14, 29, 34, 167690, tzinfo=datetime.timezone.utc)),
        ),
    ]
