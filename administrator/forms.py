from django import forms
from .models import (
    Category, MenuItem, MenuItemVariant, MenuItemAddon,
    Customer, Order, OrderItem,
    SiteSettings
)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['name', 'description', 'price', 'category', 'image', 'is_available', 'is_featured']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
        }

class MenuItemVariantForm(forms.ModelForm):
    class Meta:
        model = MenuItemVariant
        fields = ['name', 'price_adjustment', 'is_available']
        widgets = {
            'price_adjustment': forms.NumberInput(attrs={'step': '0.01'}),
        }

class MenuItemAddonForm(forms.ModelForm):
    class Meta:
        model = MenuItemAddon
        fields = ['name', 'price', 'is_available']
        widgets = {
            'price': forms.NumberInput(attrs={'step': '0.01'}),
        }

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer', 'status', 'total_price', 'payment_method', 
                  'is_paid', 'delivery_address', 'special_instructions']
        widgets = {
            'delivery_address': forms.Textarea(attrs={'rows': 3}),
            'special_instructions': forms.Textarea(attrs={'rows': 2}),
            'total_price': forms.NumberInput(attrs={'step': '0.01'}),
        }

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['menu_item', 'variant', 'quantity', 'price', 'special_instructions']
        widgets = {
            'special_instructions': forms.Textarea(attrs={'rows': 2}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
        }

class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = ['site_name', 'logo', 'contact_email', 'contact_phone', 'address',
                  'tax_rate', 'delivery_fee', 'min_order_value', 'opening_hours']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'opening_hours': forms.Textarea(attrs={'rows': 3}),
            'tax_rate': forms.NumberInput(attrs={'step': '0.01'}),
            'delivery_fee': forms.NumberInput(attrs={'step': '0.01'}),
            'min_order_value': forms.NumberInput(attrs={'step': '0.01'}),
        } 