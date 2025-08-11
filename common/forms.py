from django import forms
from common import models
from helpers import widgets
from helpers.widgets import CkeditorWidget


class SellerForm(forms.ModelForm):
    class Meta:
        model = models.Seller
        fields = ["image", "first_name", "last_name", "phone_number"]
        widgets = {
            "image": widgets.ImageInput(attrs={"id": "kt_image_3"}),
            "first_name": forms.TextInput(
                attrs={
                    "placeholder": "Ismingizni kiriting",
                    "class": "form-control",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "placeholder": "Familyangizni kiriting",
                    "class": "form-control",
                }
            ),
            "phone_number": forms.TextInput(
                attrs={
                    "placeholder": "Telefon raqamingizni kiriting",
                    "class": "form-control",
                }
            ),
 
        }

class ProductCategoryForm(forms.ModelForm):
    class Meta:
        model = models.ProductCategory
        fields = ["title"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Firma nomini kiriting"}
            )
        }



class ProductForm(forms.ModelForm):
    class Meta:
        model = models.Product
        fields = [
            "image",
            "name",
            "category",
            "entry_price",
            "price",
            "amount",
            "max_discount",
            "date_published",
        ]
        widgets = {
            "image": widgets.ImageInput(attrs={"id": "kt_image_3"}),
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Maxsulot nomini kiriting",
                    "class": "form-control",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "form-control",
                    "id": "kt_select2_2",
                }
            ),
           "entry_price": forms.TextInput(
                attrs={
                    "placeholder": "Tan narxi",
                    "class": "form-control",
                }
            ),
            "price": forms.TextInput(
                attrs={
                    "placeholder": "Narxi",
                    "class": "form-control",
                }
            ),
            "max_discount": forms.TextInput(
                attrs={
                    "placeholder": "max_discount",
                    "class": "form-control",
                }
            ),
            "amount": forms.TextInput(
                attrs={
                    "placeholder": "Maxsulot miqdori",
                    "class": "form-control",
                }
            ),
            "date_published": forms.TextInput(
                attrs={
                    "placeholder": "Kelgan sanasi",
                    "class": "form-control",
                    "type": "date"
                }
            ),
 
        }



