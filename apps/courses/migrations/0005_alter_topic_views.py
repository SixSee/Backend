# Generated by Django 4.0.2 on 2022-03-15 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_alter_course_views'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='views',
            field=models.BigIntegerField(default=0),
        ),
    ]