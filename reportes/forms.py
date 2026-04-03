from django import forms
from .models import Venta
from producto.models import Producto

class VentaForm(forms.ModelForm):
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.all(),
        widget=forms.Select(attrs={'class': 'cys-input form-select', 'id': 'productoSelect'}),
        label="Producto"
    )
    cliente = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'cys-input form-control', 'placeholder': 'Nombre del cliente'}),
        label="Cliente"
    )
    cantidad = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'cys-input form-control', 'placeholder': '0'}),
        label="Cantidad"
    )
    precio_unitario = forms.DecimalField(
        max_digits=12, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'cys-input form-control', 'placeholder': '0'}),
        label="Precio Unitario"
    )

    class Meta:
        model  = Venta
        fields = ['cliente', 'producto', 'cantidad', 'precio_unitario']