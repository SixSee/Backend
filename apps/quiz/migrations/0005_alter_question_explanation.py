# Generated by Django 4.0.2 on 2022-12-25 16:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0004_alter_questionchoice_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='explanation',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]
