# Generated by Django 5.1.3 on 2025-03-08 11:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Main', '0011_customuser_groups_customuser_is_superuser_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trainer',
            name='name',
        ),
        migrations.RemoveField(
            model_name='trainer',
            name='photo',
        ),
        migrations.AddField(
            model_name='trainer',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
