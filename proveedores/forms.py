from django import forms
from .models import Proveedor
from producto.models import Categoria


class ProveedorForm(forms.ModelForm):

    categorias_surtidas = forms.ModelMultipleChoiceField(
        queryset=Categoria.objects.filter(padre__isnull=True).order_by('nombre'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Categorías que surte",
    )

    class Meta:
        model  = Proveedor
        fields = [
            'nombre_empresa',
            'nombre_contacto',
            'email',
            'telefono',
            'categorias_surtidas',
        ]
        widgets = {
            'nombre_empresa':  forms.TextInput(attrs={'class': 'cys-input', 'placeholder': 'Ej: Distribuidora XYZ'}),
            'nombre_contacto': forms.TextInput(attrs={'class': 'cys-input', 'placeholder': 'Ej: Juan Pérez'}),
            'email':           forms.EmailInput(attrs={'class': 'cys-input', 'placeholder': 'correo@empresa.com'}),
            'telefono':        forms.TextInput(attrs={'class': 'cys-input', 'placeholder': '3001234567'}),
        }