from django import forms
from .models import Compra

class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = ['proveedor', 'producto', 'cantidad'] # No incluyas proveedor porque lo asignarás desde la vista
        widgets = {
            'producto': forms.TextInput(attrs={
                'class': 'form-control text-dark',
                'placeholder': 'Nombre del producto'
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control text-dark',
                'placeholder': 'Cantidad',
                'min': 1
            }),
        }