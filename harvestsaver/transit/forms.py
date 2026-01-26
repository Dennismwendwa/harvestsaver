from django import forms
from django.utils.translation import gettext as _

from .models import Quote, TransportBooking


class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        exclude = ["date"]

class TransportBookingForm(forms.ModelForm):
    class Meta:
        model = TransportBooking
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        order_item = cleaned_data.get("order_item")
        option = cleaned_data.get("transport_option")

        if order_item and order_item.product.is_perishable:
            if option != "express":
                raise forms.ValidationError(
                    _("Perishable goods must use Express Delivery.")
                )

        return cleaned_data
