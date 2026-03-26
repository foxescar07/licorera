from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UsuarioForm
from .models import Usuario
 
 
def lista_usuarios(request):
    usuarios = Usuario.objects.all().order_by('-fecha_registro')
    return render(request, 'lista_usuarios.html', {'usuarios': usuarios})
 
 
def registro_usuario(request):
    form = UsuarioForm()
 
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, f'Se ha registrado el nuevo usuario: {usuario.nombre}')
            return redirect('registro_usuario')
        else:
            # Un messages.error() por cada error para mostrarlos en líneas separadas
            for campo, error_list in form.errors.items():
                for error in error_list:
                    messages.error(request, error)
 
    return render(request, 'registro_usuario.html', {'form': form})
