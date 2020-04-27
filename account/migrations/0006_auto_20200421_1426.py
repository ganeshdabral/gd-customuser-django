# Generated by Django 3.0.5 on 2020-04-21 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_auto_20200421_1200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='activation_key',
            field=models.CharField(blank=True, max_length=40, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='key_expires',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
