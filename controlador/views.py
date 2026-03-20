from django.shortcuts import render
def proveedores(request):
    return render(request, 'proveedor.html')

def prueba(request):
    return render(request, 'prueba.html')


