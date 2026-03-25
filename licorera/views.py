from django.shortcuts import render, redirect

def login_proyecto(request):
    if request.method == 'POST':
        # .strip() quita espacios accidentales y .lower() pasa todo a minúsculas
        usuario = request.POST.get('usuario_input', '').strip().lower()
        clave = request.POST.get('clave_input', '').strip()

        # Probamos con "luna" y "555"
        if usuario == "luna" and clave == "555":
            # Si quieres que te mande a otra página, asegúrate de tener la URL 'home_principal'
            # Por ahora, vamos a probar que al menos te de el mensaje de éxito en la misma
            return render(request, 'login.html', {'mensaje': '¡Bienvenida Luna! Ingreso exitoso.'})
        else:
            return render(request, 'login.html', {'error': 'Credenciales incorrectas: escribiste "' + usuario + '" y "' + clave + '"'})

    return render(request, 'login.html')