# Generated by Django 3.0.8 on 2020-07-16 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='url',
            field=models.URLField(default='#', max_length=300),
        ),
    ]
