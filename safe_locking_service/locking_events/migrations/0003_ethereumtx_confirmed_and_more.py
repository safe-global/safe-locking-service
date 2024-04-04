# Generated by Django 5.0.3 on 2024-04-02 12:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("locking_events", "0002_lockevent_locking_eve_holder_f0b4de_idx"),
    ]

    operations = [
        migrations.AddField(
            model_name="ethereumtx",
            name="confirmed",
            field=models.BooleanField(default=False),
        ),
        migrations.AddIndex(
            model_name="ethereumtx",
            index=models.Index(
                condition=models.Q(("confirmed", False)),
                fields=["block_number"],
                name="Not_confirmed_block_idx",
            ),
        ),
    ]