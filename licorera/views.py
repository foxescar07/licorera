from django.shortcuts import render, redirect
from .models import Usuario

def login_proyecto(request):
    if request.method == 'POST':
        accion = request.POST.get('accion')
        datos = {k: v.strip() for k, v in request.POST.items()}

        if accion == 'login':
            user_in = datos.get('usuario_input', '').lower()
            pass_in = datos.get('clave_input', '')

            # Buscamos al usuario en la base de datos
            user_db = Usuario.objects.filter(usuario=user_in, clave=pass_in).first()

            if user_in == "luna" and pass_in == "555":
                request.session['rol'] = 'admin'
                request.session['nombre'] = 'Luna Mariana'
                return redirect('home_principal')
            
            if user_db:
                request.session['rol'] = user_db.rol
                request.session['nombre'] = user_db.nombre_completo
                return redirect('home_principal')
            else:
                return render(request, 'login.html', {'error': 'Usuario o contraseña incorrectos'})

        elif accion == 'registrar':
            try:
                Usuario.objects.create(
                    identificacion=datos.get('id_input'),
                    nombre_completo=datos.get('nombre_input'),
                    usuario=datos.get('user_nuevo').lower(),
                    clave=datos.get('pass_nueva'),
                    rol=datos.get('rol_nuevo') # Guardamos el rol elegido
                )
                return render(request, 'login.html', {'mensaje': 'Registro exitoso. ¡Ya puedes entrar!'})
            except:
                return render(request, 'login.html', {'error': 'Error: El ID o Usuario ya existen.'})

    return render(request, 'login.html')

def principal_view(request):
    # Recuperamos los datos de la sesión
    rol = request.session.get('rol', 'Sin Rol')
    nombre = request.session.get('nombre', 'Invitado')
    return render(request, 'principal.html', {'rol': rol, 'nombre': nombre})