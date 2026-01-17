from django import forms
from django.forms import Textarea
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

from accounts.models import User
from .models import (Product, Equipment, EquipmentInquiry,
                     )


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ["slug", "is_available",]
        labels = {
            "name": _("Product name"),
            "category": _("Category"),
            "price": _("price per unit"),
            "quantity": _("Quantity available"),
            "unit_of_measurement": _("Unit_of_measurement"),
            "description": _("Product description"),
            "image": _("Image"),
            "location": _("location"),
            "harvest_date": _("harvest_date"),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields["owner"].queryset = User.objects.filter(pk=user.pk)
    
    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        
        if name:
            slug = slugify(name)
            cleaned_data["slug"] = slug
        
        return cleaned_data

class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        exclude = ["slug", "is_available"]
        labals = {
            "name": _("Equipment name"),
            "description": _("Product description"),
            "category": _("Category"),
            "image": _("Image"),
            "location": _("location"),
            "price": _("price per hour"),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields["owner"].queryset = User.objects.filter(pk=user.pk)

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")

        if name:
            slug = slugify(name)
            cleaned_data["slug"] = slug

        return cleaned_data


class EquipmentInquiryForm(forms.ModelForm):
    class Meta:
        model = EquipmentInquiry
        exclude = ["date", "admin_responded",]




























