# Generated by Django 4.0.6 on 2022-08-03 13:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='image',
        ),
    ]
