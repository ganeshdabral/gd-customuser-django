# Generated by Django 3.0.5 on 2020-04-16 13:09

import account.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=account.models.user_img_upload),
        ),
    ]
