# Generated by Django 3.1.1 on 2022-09-04 13:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('short', '0002_urldetail'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='urldetail',
            name='user',
        ),
    ]
