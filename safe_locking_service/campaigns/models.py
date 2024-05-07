from django.db import models


class Campaign(models.Model):
    id = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.CharField(blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Campaign {self.id} {self.name}"
