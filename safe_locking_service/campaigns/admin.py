from django.contrib import admin

from .models import Campaign


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "start_date", "end_date")
    search_fields = ("name",)
    fields = ("name", "description", "start_date", "end_date")
