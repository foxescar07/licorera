from django.shortcuts import render


def home(request):
        nombre = 'cristian'
        context = {
        'nombre': nombre,
        'titulo': 'Home'
    }
        return render(request, 'usuario.html', context)
    
def proveedores(request):
    return render(request, 'proveedor.html')

def reportes(request):
    return render(request, 'reportes.html')

def prueba(request):
    return render(request, 'prueba.html')

def dashboard(request):
    return render(request, 'dashboard.html')