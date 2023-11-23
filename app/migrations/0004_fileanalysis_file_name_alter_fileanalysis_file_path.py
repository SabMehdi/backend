# Generated by Django 4.2.7 on 2023-11-23 18:26

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_fileanalysis_file_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='fileanalysis',
            name='file_name',
            field=models.FilePathField(default=django.utils.timezone.now, path='uploads/', recursive=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='fileanalysis',
            name='file_path',
            field=models.CharField(max_length=1024),
        ),
    ]
