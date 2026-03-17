from django import forms
from .models import Producto, Categoria


class ProductoForm(forms.ModelForm):
    """
    Formulario para registrar y editar un Producto.
    Conectado al modal 'modalNuevoProducto' del HTML.
    """

    class Meta:
        model  = Producto
        fields = [
            "codigo",
            "nombre",
            "descripcion",
            "categoria",
            "precio_unitario",
            "cantidad_disponible",
            "unidad",
        ]
        widgets = {
            # --- Campos de texto ---
            "nombre": forms.TextInput(attrs={
                "class":       "form-control",
                "placeholder": "Ej: Aguila Lata 330ml",
                "id":          "nombreProducto",
            }),
            "codigo": forms.TextInput(attrs={
                "class":       "form-control",
                "placeholder": "Ej: AGU330",
                "id":          "codigo",
            }),
            "descripcion": forms.Textarea(attrs={
                "class":       "form-control",
                "rows":        3,
                "placeholder": "Ej: Cerveza nacional, lata 330ml, six pack...",
                "id":          "descripcion",
            }),
            # --- Selects ---
            "categoria": forms.Select(attrs={
                "class": "form-select",
                "id":    "categoria",
            }),
            "unidad": forms.Select(attrs={
                "class": "form-select",
                "id":    "unidad",
            }),
            # --- Numéricos ---
            "precio_unitario": forms.NumberInput(attrs={
                "class":       "form-control",
                "placeholder": "45000",
                "min":         "0",
                "step":        "100",
                "id":          "precio",
            }),
            "cantidad_disponible": forms.NumberInput(attrs={
                "class":       "form-control",
                "placeholder": "50",
                "min":         "0",
                "id":          "stockInicial",
            }),
        }
        labels = {
            "nombre":              "Nombre del Producto",
            "codigo":              "Código / Referencia",
            "descripcion":         "Descripción (opcional)",
            "categoria":           "Categoría",
            "precio_unitario":     "Precio Unitario (COP)",
            "cantidad_disponible": "Stock Inicial",
            "unidad":              "Unidad",
        }