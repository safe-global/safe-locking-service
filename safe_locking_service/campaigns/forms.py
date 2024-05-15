from django import forms

from .models import Period


class FileUploadForm(forms.Form):
    period = forms.ModelChoiceField(
        queryset=Period.objects.none(),
        empty_label="Choose a Campaign Period",
    )
    file = forms.FileField()

    def __init__(self, *args, **kwargs):
        period_slug = kwargs.pop("period_slug", None)
        super().__init__(*args, **kwargs)
        if period_slug is not None:
            self.fields["period"].queryset = Period.objects.filter(slug=period_slug)
            self.fields["period"].empty_label = None
        else:
            self.fields["period"].queryset = Period.objects.order_by("-start_date")
