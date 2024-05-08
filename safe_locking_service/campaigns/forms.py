from django import forms

from .models import Period


class FileUploadForm(forms.Form):
    period = forms.ModelChoiceField(
        queryset=Period.objects.order_by("-start_date"),
        empty_label="Choose a Campaign Period",
    )
    file = forms.FileField()
