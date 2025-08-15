from django import forms
from common import models
from helpers import widgets
from helpers.widgets import CkeditorWidget

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = models.CustomUser
        fields = [
            'first_name',
            'last_name',
            "username",
            "phone",
            'email',
            "role",
            "password",
            "seller_profile",
        ]
        widgets = {
            'first_name' : forms.TextInput(attrs={"class": "form-control"}),
            'last_name' : forms.TextInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control", "autocomplete" : "off"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-control", "id": "kt_select2_3"}),
            "password": forms.PasswordInput(attrs={"class": "form-control", "autocomplete" : "off"}),
            'seller_profile' : forms.Select(attrs={"class" : "form-control", "id" : "kt_select2_2"})
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_active = True
        if commit:
            user.save()
        return user

class CustomUserInfoForm(forms.ModelForm):
    class Meta:
        model = models.CustomUser
        fields = [
            'first_name',
            'last_name',
            "username",
            "phone",
            'email',
        ]
        widgets = {
            'first_name' : forms.TextInput(attrs={"class": "form-control"}),
            'last_name' : forms.TextInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control", "autocomplete" : "off"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.is_active = True
        if commit:
            user.save()
        return user


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


class CashRegisterForm(forms.ModelForm):
    class Meta:
        model = models.CashRegister
        fields = ["user", "total_cash", "total_card", "total_sales", "opened_at"]
        widgets = {
            "total_cash": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "user": forms.Select(
                attrs={
                    "class": "form-control",
                    "id": "kt_select2_2",
                }
            ),
            "total_card": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "total_sales": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "opened_at": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),
            "closed_at": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),
        }

class CashFlowCategoryForm(forms.ModelForm):
    class Meta:
        model = models.CashFlowCategory
        fields=['title']
        widgets ={
            'title': forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            )
        }


class CashFlowForm(forms.ModelForm):
    class Meta:
        model = models.CashFlow
        fields=['cash_register', 'flow_type', 'amount', 'category', 'created_at']
        widgets ={
            'cash_register': forms.Select(
                    attrs={
                        "class": 'form-control'
                }
            ),
            'flow_type': forms.Select(
                    attrs={
                        "class": 'form-control'
                }
            ),
            'amount': forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            'category': forms.Select(
                    attrs={
                        "class": 'form-control'
                }
            ),
            'created_at': forms.DateTimeInput(
            attrs={
                "class": "form-control",
                "type": 'date'
            }
        ),
    }
