# Generated by Django 3.0.8 on 2020-10-29 09:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CMSApp', '0003_auto_20201029_1309'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_deleted',
        ),
    ]
