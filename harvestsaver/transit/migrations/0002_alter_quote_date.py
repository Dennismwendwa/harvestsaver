# Generated by Django 4.2.7 on 2023-11-25 06:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transit', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quote',
            name='date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]