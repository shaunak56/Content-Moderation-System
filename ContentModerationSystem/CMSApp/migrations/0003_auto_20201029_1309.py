# Generated by Django 3.0.8 on 2020-10-29 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CMSApp', '0002_remove_tier_created_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='access_key',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='account_id',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
