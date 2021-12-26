# Generated by Django 2.2.5 on 2021-12-26 04:31

import apps.users.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20211224_2013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatarPath',
            field=models.ImageField(default='http://localhost:8082/media/upload/userAvatar/default.png', max_length=300, null=True, upload_to=apps.users.models.user_directory_path, verbose_name='头像'),
        ),
    ]