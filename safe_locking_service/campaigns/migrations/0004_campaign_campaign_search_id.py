# Generated by Django 5.0.4 on 2024-05-15 10:54

from django.db import migrations, models
from django.utils.text import slugify


def generate_unique_campaign_search_id(apps, schema_editor):
    Campaign = apps.get_model("campaigns", "Campaign")
    for obj in Campaign.objects.all():
        obj.slug_field = slugify(obj.name)
        obj.save()


class Migration(migrations.Migration):
    dependencies = [
        ("campaigns", "0003_activitymetadata"),
    ]

    operations = [
        migrations.AddField(
            model_name="campaign",
            name="campaign_search_id",
            field=models.SlugField(unique=True, db_index=True, blank=True),
            preserve_default=False,
        ),
        migrations.RunPython(generate_unique_campaign_search_id),
    ]
