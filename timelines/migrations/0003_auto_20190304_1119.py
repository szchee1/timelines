# Generated by Django 2.1.7 on 2019-03-04 03:19

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timelines', '0002_auto_20190303_1644'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalweeks',
            name='agency_capacity',
            field=models.FloatField(default=75, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='historicalweeks',
            name='analytics_capacity',
            field=models.FloatField(default=75, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='historicalweeks',
            name='ops_capacity',
            field=models.FloatField(default=75, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='weeks',
            name='agency_capacity',
            field=models.FloatField(default=75, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='weeks',
            name='analytics_capacity',
            field=models.FloatField(default=75, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='weeks',
            name='ops_capacity',
            field=models.FloatField(default=75, validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
