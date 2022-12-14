# Generated by Django 2.2.5 on 2021-12-31 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0008_auto_20211231_1046'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='value',
            field=models.CharField(default='', max_length=20, verbose_name='标签值'),
        ),
        migrations.AddField(
            model_name='type',
            name='value',
            field=models.CharField(default='学习日志', max_length=20, verbose_name='分类值'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(default='', max_length=20, primary_key=True, serialize=False, verbose_name='标签'),
        ),
    ]
