from django import forms

from .models import IssueRecord, TransferRecord

class IssueRecordForm(forms.ModelForm):
    class Meta:
        model = IssueRecord
        exclude = ["issued_by", "issued_a"]


class TransferRecordForm(forms.ModelForm):
    class Meta:
        model = TransferRecord
        exclude = ["sent_at", "received_at", "status", ]

    def __init__(self, *args, **kwargs):
        super(TransferRecordForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control my-2",})