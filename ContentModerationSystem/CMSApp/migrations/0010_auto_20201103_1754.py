# Generated by Django 3.1.3 on 2020-11-03 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CMSApp', '0009_auto_20201103_1124'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contentgroup',
            name='report_status',
            field=models.CharField(choices=[('1', 'Complete'), ('2', 'Incomplete'), ('3', 'Error')], default=2, max_length=200),
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='first name'),
        ),
    ]
