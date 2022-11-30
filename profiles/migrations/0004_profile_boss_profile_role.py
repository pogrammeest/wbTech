# Generated by Django 4.0.6 on 2022-11-26 09:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0003_alter_profile_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='boss',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='slaves', to=settings.AUTH_USER_MODEL, verbose_name='Начальник'),
        ),
        migrations.AddField(
            model_name='profile',
            name='role',
            field=models.CharField(choices=[('OE', 'Рядовой сотрудник'), ('HOD', 'Руководитель подразделения')], default='OE', max_length=30, verbose_name='Роль'),
        ),
    ]