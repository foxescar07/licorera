from django.shortcuts import render, redirect
from .forms import ProveedorForm
from .models import Proveedor

def inicio_proveedores(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save() # Aquí se guarda el proveedor
            return redirect('proveedores') # Esto refresca la página
    else:
        form = ProveedorForm() 
    
    proveedores = Proveedor.objects.all()
    
    context={
        'form': form,
        'proveedores': proveedores
    }
    return render(request, 'proveedor.html', context)