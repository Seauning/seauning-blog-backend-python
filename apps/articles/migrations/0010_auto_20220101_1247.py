# Generated by Django 2.2.5 on 2022-01-01 04:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0009_auto_20211231_1450'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='state',
            field=models.CharField(blank=True, choices=[('byself', '原创'), ('byother', '转载')], max_length=20, verbose_name='状态'),
        ),
    ]