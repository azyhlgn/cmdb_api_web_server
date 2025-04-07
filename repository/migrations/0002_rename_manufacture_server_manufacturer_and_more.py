# Generated by Django 5.1.7 on 2025-04-07 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='server',
            old_name='manufacture',
            new_name='manufacturer',
        ),
        migrations.AlterField(
            model_name='disk',
            name='model',
            field=models.CharField(max_length=128, verbose_name='硬盘型号'),
        ),
        migrations.AlterField(
            model_name='nic',
            name='up',
            field=models.CharField(default=False, max_length=32, verbose_name='网卡状态'),
        ),
    ]
