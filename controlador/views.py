from django.shortcuts import render

def proveedores(request):
    return render(request, 'proveedor.html')

def reportes(request):
    return render(request, 'reportes.html')

def prueba(request):
    return render(request, 'prueba.html')

