# Generated by Django 4.2.5 on 2023-11-04 23:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_fileanalysis_file_hash'),
    ]

    operations = [
        migrations.AddField(
            model_name='fileanalysis',
            name='file_content',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
    ]
