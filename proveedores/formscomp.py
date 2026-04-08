from django import forms
from .models import Compra, Producto


class CompraForm(forms.ModelForm):
    proveedor = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Compra
        fields = [ 'producto', 'cantidad']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        proveedor_id = kwargs.pop('proveedor_id', None)
        super().__init__(*args, **kwargs)

        # cargar proveedores
        from .models import Proveedor
        self.fields['proveedor'].queryset = Proveedor.objects.all()

        # filtrar productos
        if proveedor_id:
            self.fields['producto'].queryset = Producto.objects.filter(proveedor_id=proveedor_id)
        else:
            self.fields['producto'].queryset = Producto.objects.none()