# Generated by Django 4.0.2 on 2022-07-09 16:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0003_userattemptedquestion_user_quiz_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='questionchoice',
            options={'ordering': ['pk']},
        ),
    ]
