# Generated by Django 5.0.6 on 2024-06-03 08:27

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("campaigns", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="period",
            options={
                "permissions": [
                    ("upload_activities", "Can upload activities for the given period")
                ]
            },
        ),
    ]
