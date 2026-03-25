from django.shortcuts import render

def login_proyecto(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario_input', '').strip().lower()
        clave = request.POST.get('clave_input', '').strip()

        if usuario == "LUNA" and clave == "555":
            return render(request, 'login.html', {'mensaje': '¡Bienvenida Luna! Ingreso exitoso.'})
        else:
            return render(request, 'login.html', {'error': 'Credenciales incorrectas'})

    return render(request, 'login.html')