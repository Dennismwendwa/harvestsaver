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
            "price": _("Price per unit"),
            "quantity": _("Available quantity"),
            "unit_quantity_type": _("Unit"),
            "unit_weight_kg": _("Weight per unit (kg)"),
            "description": _("Description"),
            "image": _("Product image"),
            "harvest_date": _("Harvest date"),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            base_classes = "form-control form-control-lg"

            # Text inputs
            if isinstance(field.widget, forms.TextInput):
                field.widget.attrs.update({
                    "class": base_classes,
                    "placeholder": field.label
                })

            # Number inputs
            elif isinstance(field.widget, forms.NumberInput):
                field.widget.attrs.update({
                    "class": base_classes,
                    "placeholder": field.label
                })
                if name == "unit_weight_kg":
                    field.widget.attrs.update({
                        "min": "0.01",
                        "step": "0.01"
                    })

            # Selects
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({
                    "class": "form-select form-select-lg"
                })

            # File upload
            elif isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs.update({
                    "class": "form-control"
                })

            # Textarea
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Enter " + field.label.lower()
                })

        # Date picker
        self.fields["harvest_date"].widget = forms.DateInput(
            attrs={
                "class": "form-control form-control-lg",
                "type": "date",
            }
        )

        # Farm filtering
        if self.user:
            self.fields["farm"].queryset = Farm.objects.filter(
                owner=self.user,
                is_verified=True
            )

        self.fields["farm"].label_from_instance = lambda obj: obj.name


    def clean_form(self):
        farm = self.cleaned_data.get("farm")

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
    
    def clean_unit_weight_kg(self):
        weight = self.cleaned_data.get("unit_weight_kg")
        if weight is not None and weight <= 0:
            raise forms.ValidationError("Unit weight must be greater than 0 kg.")
        return weight

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

        for name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control my-2",})
            
            base_classes = "form-control form-control-lg"

            if isinstance(field.widget, forms.NumberInput):
                field.widget.attrs.update({
                    "class": base_classes,
                    "placeholder": f"Enter {field.label.lower()}"
                })

                if name == "price_per_hour":
                    field.widget.attrs.update({
                        "min": "1",
                        "step": "1"
                    })
    
    def clean_price_per_hour(self):
        price = self.cleaned_data.get("price_per_hour")
        if price is not None and price <= 0:
            raise forms.ValidationError(_("Price per hour must be greater than 1"))
        return price

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
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Staff can see everything
        if self.user and self.user.is_staff:
            self.fields["owner"] = forms.ModelChoiceField(
                queryset=User.objects.filter(
                    farmer_profile__isnull=False,
                    is_active=True, ),
                required=True,
                label="Farmer"
            )
            self.fields["owner"].label_from_instance = lambda obj: obj.username

            self.fields["hub"] = forms.ModelChoiceField(
                queryset=Hub.objects.all(),
                required=False
            )
            self.fields["is_verified"] = forms.BooleanField(
                required=False
            )

        for field_name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control my-2",})


class HubForm(forms.ModelForm):
    class Meta:
        model = Hub
        fields = ["name", "location", "latitude", "longitude", "radius_km"]
        widgets = {
            "latitude": forms.HiddenInput(),
            "longitude": forms.HiddenInput(),
        }

