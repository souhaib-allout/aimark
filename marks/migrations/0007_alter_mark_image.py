# Generated by Django 3.2.8 on 2022-05-06 23:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marks', '0006_alter_mark_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mark',
            name='image',
            field=models.ImageField(upload_to='marks'),
        ),
    ]
