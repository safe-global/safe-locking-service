from django.contrib import admin

from .models import Activity, ActivityMetadata, Campaign, Period


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("uuid", "name", "start_date", "end_date")
    search_fields = ("name",)
    fields = (
        "name",
        "description",
        "start_date",
        "end_date",
    )


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = (
        "campaign",
        "slug",
        "start_date",
        "end_date",
    )
    search_fields = ("campaign",)
    fields = (
        "campaign",
        "start_date",
        "end_date",
    )


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = (
        "period",
        "address",
        "total_points",
        "boost",
        "total_boosted_points",
    )
    search_fields = ("address",)


@admin.register(ActivityMetadata)
class ActivityMetadataAdmin(admin.ModelAdmin):
    list_display = ("name", "campaign_name", "description", "max_points")
    list_select_related = ("campaign",)
    search_fields = ("name", "campaign__name")
    fields = (
        "campaign",
        "name",
        "description",
        "max_points",
    )

    def campaign_name(self, obj):
        return obj.campaign.name
