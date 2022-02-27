from django import forms
from django.db.models.base import Model
from django.forms import widgets
from django.forms.fields import ChoiceField
from django.forms.models import ModelForm
from django.forms.widgets import Widget
from .models import Address, Donateme, Aboutme
from django.utils.translation import gettext_lazy as _


class AddProduct(forms.Form):
    name = forms.CharField(label="Name", max_length=50, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-lg'}))
    sell_price = forms.CharField(label="Selling Price", max_length=10, widget=forms.NumberInput(
        attrs={'class': 'form-control form-control-lg'}))
    buy_price = forms.CharField(label="Buying Price", max_length=10, widget=forms.NumberInput(
        attrs={'class': 'form-control form-control-lg'}))
    sale_price = forms.CharField(label="Sale Price", max_length=10, widget=forms.NumberInput(
        attrs={'class': 'form-control form-control-lg'}), required=False)

    CATEGORY = (('Vegetables', 'Vegetables'),
                ('Fruits', 'Fruits'), ('Grains', 'Grains'))
    category = forms.ChoiceField(
        choices=CATEGORY, widget=forms.Select(attrs={'class': 'form-control'}))

    description = forms.CharField(label="Description", widget=forms.Textarea(
        attrs={'class': 'form-control form-control-lg'}))
    CHOICES = (('1', 'Yes'), ('2', 'No'))
    in_stock = forms.ChoiceField(choices=CHOICES, widget=forms.Select(
        attrs={'class': 'form-control '}), required=True)
    # in_stock.widget.attrs.update({'class': 'list-unstyled d-flex'})
    IMG_UPLOAD_CHOICE = (('1', 'Load from URL'), ('2', 'Upload an Image'))
    upload_choice = forms.ChoiceField(choices=IMG_UPLOAD_CHOICE, widget=forms.Select(
        attrs={'class': 'form-control', 'id': 'img_choice', 'onchange': 'onSelectChange()'}), required=False)
    img = forms.ImageField(widget=forms.FileInput(attrs={
                           'class': 'form-control-lg form-control-file', 'id': 'browse', 'disabled': True}), required=False)
    img_url = forms.URLField(widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg', 'id': 'url', 'placeholder': 'Enter Url'}), required=False)


class AddressForm(ModelForm):
    class Meta:
        model = Address
        exclude = ['user']
        labels = {
            'address_line1': _('Addres 1'),
            'address_line2': _('Addres 2'),
        }
        widgets = {
            "country": forms.Select(attrs={'class': 'form-control selectpicker country', 'id': 'country'})
        }


class DonatemeForm(ModelForm):
    IMG_UPLOAD_CHOICE = (('1', 'Load from URL'), ('2', 'Upload an Image'))
    upload_choice = forms.ChoiceField(choices=IMG_UPLOAD_CHOICE, widget=forms.Select(
        attrs={'class': 'form-control', 'id': 'img_choice', 'onchange': 'onSelectChange()'}), required=False)
    img = forms.ImageField(widget=forms.FileInput(attrs={
                           'class': 'form-control-lg form-control-file', 'id': 'browse', 'disabled': True}), required=False)
    img_url = forms.URLField(widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg', 'id': 'url', 'placeholder': 'Enter Url'}), required=False)

    class Meta:
        model = Donateme
        exclude = ['farmer', 'is_active']

class AboutmeForm(ModelForm):
    IMG_UPLOAD_CHOICE = (('1', 'Load from URL'), ('2', 'Upload an Image'))
    upload_choice = forms.ChoiceField(choices=IMG_UPLOAD_CHOICE, widget=forms.Select(
        attrs={'class': 'form-control', 'id': 'img_choice', 'onchange': 'onSelectChange()'}), required=False)
    img = forms.ImageField(widget=forms.FileInput(attrs={
                           'class': 'form-control-lg form-control-file', 'id': 'browse', 'disabled': True}), required=False)
    img_url = forms.URLField(widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg', 'id': 'url', 'placeholder': 'Enter Url'}), required=False)

    class Meta:
        model = Aboutme
        exclude = ['farmer', 'is_verified']
