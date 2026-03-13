from django.shortcuts import render
from .models import Proveedor

def proveedores(request):
    proveedores = Proveedor.objects.all()
    return render(request, 'proveedores/proveedor.html', {
        'proveedores': proveedores
    })