# Generated by Django 3.2.8 on 2022-05-06 23:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marks', '0004_alter_mark_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mark',
            name='image',
            field=models.ImageField(upload_to='marks'),
        ),
    ]