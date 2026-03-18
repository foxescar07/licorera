from django.shortcuts import render

# Create your views here.
def proveedores(request):
    return render(request, 'proveedor.html')

def prueba(request):
    return render(request, 'prueba.html')


