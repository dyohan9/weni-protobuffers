# Generated by Django 2.2.19 on 2021-07-05 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0004_auto_20210702_1456"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="last_update_profile",
            field=models.DateTimeField(null=True, verbose_name="Last Updated Profile"),
        ),
    ]
