from django.shortcuts import render

# Create your views here.
def proveedores(request):
    return render(request, 'proveedor.html')

def producto(request):
    return render(request, 'producto.html')