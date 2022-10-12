from django import forms
from django.forms import fields

from .models import BaseProductModel


class BaseProductModelForm(forms.ModelForm):
    class Meta:
        model = BaseProductModel
        fields = [
            'name',
            'barcode',
            'piece',
        ]