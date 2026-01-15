from django import forms
from .models import Contact
from .models import FarmerProfile, BuyerProfile, EquipmentOwnerProfile

BASE_INPUT_CLASS = "form-control"
BASE_TEXTAREA_CLASS = "form-control"
BASE_CHECKBOX_CLASS = "form-check-input"

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        exclude = ["date"]

class EquipmentOwnerProfileForm(forms.ModelForm):
    class Meta:
        model = EquipmentOwnerProfile
        exclude = ["user"]
        widgets = {
            "image": forms.ClearableFileInput(attrs={
                "class": BASE_INPUT_CLASS
            }),
            "bio": forms.Textarea(attrs={
                "class": BASE_TEXTAREA_CLASS,
                "rows": 4,
                "placeholder": "Tell people about yourself..."
            }),
            "facebook_username": forms.TextInput(attrs={
                "class": BASE_INPUT_CLASS,
                "placeholder": "Facebook username"
            }),
            "instagram_username": forms.TextInput(attrs={
                "class": BASE_INPUT_CLASS,
                "placeholder": "Instagram username"
            }),
            "notification": forms.CheckboxInput(attrs={
                "class": BASE_CHECKBOX_CLASS
            }),
        }


class FarmerProfileForm(forms.ModelForm):
    class Meta:
        model = FarmerProfile
        exclude = ["user"]
        widgets = {
            "image": forms.ClearableFileInput(attrs={
                "class": BASE_INPUT_CLASS
            }),
            "bio": forms.Textarea(attrs={
                "class": BASE_TEXTAREA_CLASS,
                "rows": 4
            }),
            "farm_name": forms.TextInput(attrs={
                "class": BASE_INPUT_CLASS,
                "placeholder": "Farm name"
            }),
            "farm_size": forms.TextInput(attrs={
                "class": BASE_INPUT_CLASS,
                "placeholder": "e.g. 5 acres"
            }),
            "location": forms.TextInput(attrs={
                "class": BASE_INPUT_CLASS,
                "placeholder": "Farm location"
            }),
            "crop_types": forms.TextInput(attrs={
                "class": BASE_INPUT_CLASS,
                "placeholder": "Maize, Beans, Wheat"
            }),
            "facebook_username": forms.TextInput(attrs={
                "class": BASE_INPUT_CLASS
            }),
            "instagram_username": forms.TextInput(attrs={
                "class": BASE_INPUT_CLASS
            }),
            "notification": forms.CheckboxInput(attrs={
                "class": BASE_CHECKBOX_CLASS
            }),
        }


class BuyerProfileForm(forms.ModelForm):
    class Meta:
        model = BuyerProfile
        exclude = ["user"]
        widgets = {
            "image": forms.ClearableFileInput(attrs={
                "class": BASE_INPUT_CLASS
            }),
            "bio": forms.Textarea(attrs={
                "class": BASE_TEXTAREA_CLASS,
                "rows": 4
            }),
            "location": forms.TextInput(attrs={
                "class": BASE_INPUT_CLASS,
                "placeholder": "Your location"
            }),
            "preferred_categories": forms.TextInput(attrs={
                "class": BASE_INPUT_CLASS,
                "placeholder": "Grains, Vegetables, Equipment"
            }),
            "facebook_username": forms.TextInput(attrs={
                "class": BASE_INPUT_CLASS
            }),
            "instagram_username": forms.TextInput(attrs={
                "class": BASE_INPUT_CLASS
            }),
            "notification": forms.CheckboxInput(attrs={
                "class": BASE_CHECKBOX_CLASS
            }),
        }


