# Generated by Django 4.2.9 on 2024-01-09 03:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scraper', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='firmware',
            name='file_path',
            field=models.CharField(max_length=500, unique=True, verbose_name='固件路径'),
        ),
        migrations.AlterField(
            model_name='firmware',
            name='url_hash',
            field=models.CharField(db_index=True, max_length=100, verbose_name='下载地址hash'),
        ),
    ]