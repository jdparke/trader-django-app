# Generated by Django 2.1.5 on 2022-03-23 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menus', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='menu',
            name='isActive',
            field=models.BooleanField(default=False),
        ),
    ]
