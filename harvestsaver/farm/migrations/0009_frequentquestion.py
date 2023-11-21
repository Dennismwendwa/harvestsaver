# Generated by Django 4.2.7 on 2023-11-21 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('farm', '0008_review'),
    ]

    operations = [
        migrations.CreateModel(
            name='FrequentQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField()),
                ('answer', models.TextField()),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Frequent Question',
                'verbose_name_plural': 'Frequest Questions',
                'ordering': ('-pk',),
                'unique_together': {('question', 'answer')},
            },
        ),
    ]