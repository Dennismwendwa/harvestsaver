from django import forms
from django.forms import Textarea
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

from accounts.models import User
from .models import (Product, Equipment, EquipmentInquiry, Farm, Hub,
                     )


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ["slug", "is_available", "hub",]
        widgets = {
            "description": forms.Textarea(attrs={
                "rows": 2,
                "placeholder": "Enter product description ...",
                "class": "form-control mt-2",
            }),
        }
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
        self.user = kwargs.pop("user", None)
        super(ProductForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control my-2",})

        self.fields["harvest_date"].widget = forms.DateInput(
            attrs={
            "class": "form-control my-2",
            "placeholder": "Select harvest date",
            "type": "date",
            }
        )
        
        if self.user:
            self.fields["farm"].queryset = Farm.objects.filter(owner=self.user,
                                                               is_verified=True)

    def clean_form(self):
        farm = self.cleaned_dats.get("farm")

        if not farm:
            raise forms.ValidationError(_("You must select a farm"))
        
        if self.user and farm.owner != self.user:
            raise forms.ValidationError(_("You do not own this farm"))
        
        if not farm.is_verified:
            raise forms.ValidationError(_("This farm is not verified yet."))
        
        return farm
    
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

class FarmForm(forms.ModelForm):
    class Meta:
        model = Farm
        exclude = ["owner", "hub", "is_verified"]

        widgets = {
            "address": forms.Textarea(attrs={
                "rows": 2,
                "placeholder": "Enter farms address here...",
                "class": "form-control mt-2",
            }),
        }


    def __init__(self, *args, **kwargs):
        super(FarmForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control my-2",})


class HubForm(forms.ModelForm):
    class Meta:
        model = Hub
        fields = ["name", "county", "latitude", "longitude", "radius_km"]
        widgets = {
            "latitude": forms.HiddenInput(),
            "longitude": forms.HiddenInput(),
        }

