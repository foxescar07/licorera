from django.shortcuts import render

# Create your views here.
def proveedores(request):
    return render(request, 'proveedor.html')
def usuario(request):
    return render(request, 'usuario.html')

