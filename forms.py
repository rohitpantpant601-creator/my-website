from django import forms
from .models import Order

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'email', 'phone', 'address', 'payment_method']
        widgets = {
            'payment_method': forms.RadioSelect(), # Radio buttons for selection
        }