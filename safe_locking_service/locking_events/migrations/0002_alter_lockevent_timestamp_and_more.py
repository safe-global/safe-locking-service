# Generated by Django 4.2.10 on 2024-03-13 13:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("locking_events", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="lockevent",
            name="timestamp",
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name="unlockevent",
            name="timestamp",
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name="withdrawnevent",
            name="timestamp",
            field=models.DateTimeField(db_index=True),
        ),
    ]
