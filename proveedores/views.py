from django.shortcuts import render

def home(request):
    nombre = 'cristian'
    context = {
        'nombre': nombre,
        'titulo': 'Home'
    }
    return render(request, 'home.html', context)


def proveedor(request):
    return render(request, 'proveedor.html')

def proveedores(request):
    return render(request, 'proveedor.html')
