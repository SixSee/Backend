# Generated by Django 4.0.2 on 2022-03-14 05:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_course_is_archived_alter_course_slug_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='views',
            field=models.BigIntegerField(default=0),
        ),
    ]