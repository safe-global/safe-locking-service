# Generated by Django 5.0.6 on 2024-06-17 12:38

from django.db import migrations, models

import safe_locking_service.campaigns.models


class Migration(migrations.Migration):

    dependencies = [
        ("campaigns", "0004_alter_activity_options"),
    ]

    operations = [
        migrations.CreateModel(
            name="Partner",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50, unique=True)),
                (
                    "logo",
                    models.ImageField(
                        upload_to=safe_locking_service.campaigns.models.logo_path
                    ),
                ),
                (
                    "campaigns",
                    models.ManyToManyField(
                        related_name="partners", to="campaigns.campaign"
                    ),
                ),
            ],
        ),
    ]
