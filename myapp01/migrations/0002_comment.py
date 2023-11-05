# Generated by Django 4.2.6 on 2023-10-16 11:30

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp01', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('idx', models.AutoField(primary_key=True, serialize=False)),
                ('board_idx', models.IntegerField()),
                ('writer', models.CharField(max_length=50)),
                ('content', models.TextField()),
                ('post_date', models.DateTimeField(blank=True, default=datetime.datetime.now)),
            ],
        ),
    ]
