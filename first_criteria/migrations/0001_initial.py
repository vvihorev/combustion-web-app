# Generated by Django 4.0.4 on 2022-04-28 21:42

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Engine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(default='some Engine')),
                ('nu', models.IntegerField(default='0')),
            ],
        ),
    ]
