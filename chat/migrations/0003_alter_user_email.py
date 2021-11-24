# Generated by Django 3.2.9 on 2021-11-24 13:57

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_auto_20211124_0150'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=40, unique=True, validators=[django.core.validators.EmailValidator()]),
        ),
    ]