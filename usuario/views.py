from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from .models import Usuario
from .forms import UsuarioForm
import hashlib


def login_view(request):
    if request.session.get('usuario_id'):
        return redirect('home')

    if request.method == 'POST':
        usuario_input = request.POST.get('usuario_input', '').strip()
        clave_input   = request.POST.get('clave_input', '')
        clave_hash    = hashlib.sha256(clave_input.encode()).hexdigest()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                usuario = Usuario.objects.get(
                    usuario=usuario_input, clave=clave_hash, activo=True
                )
                request.session['usuario_id']     = usuario.pk
                request.session['usuario_nombre'] = usuario.nombre_completo
                request.session['usuario_rol']    = usuario.rol
                request.session['usuario_user']   = usuario.usuario
                return JsonResponse({'ok': True, 'redirect': '/'})
            except Usuario.DoesNotExist:
                return JsonResponse({'ok': False, 'error': 'Usuario o contraseña incorrectos.'})

    return render(request, 'usuario.html')


def logout_view(request):
    request.session.flush()
    return redirect('login')


def lista_usuarios(request):
    if not request.session.get('usuario_id'):
        return redirect('login')
    usuarios = Usuario.objects.all().order_by('-fecha_registro')
    return render(request, 'usuarios_lista.html', {'usuarios': usuarios})


def crear_usuario(request):
    form = UsuarioForm()

    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            u = form.save()
            return render(request, 'crear_usuario.html', {
                'form': form,
                'usuario_creado': True,
                'nuevo_usuario': u.usuario,
            })
        else:
            for campo, errores in form.errors.items():
                for error in errores:
                    messages.error(request, error)

    return render(request, 'crear_usuario.html', {'form': form})


def solicitar_recuperacion(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        correo = request.POST.get('correo', '').strip().lower()

        try:
            usuario = Usuario.objects.get(email__iexact=correo, activo=True)
        except Usuario.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'No existe una cuenta activa con ese correo.'})

        token = get_random_string(32)
        request.session[f'reset_token_{token}'] = usuario.pk

        link = request.build_absolute_uri(f'/usuario/restablecer/{token}/')

        try:
            send_mail(
                subject='Recuperación de contraseña — CYS Ltda',
                message=(
                    f'Hola {usuario.nombre},\n\n'
                    f'Recibimos una solicitud para restablecer tu contraseña.\n\n'
                    f'Haz clic en el siguiente enlace para crear una nueva contraseña:\n{link}\n\n'
                    f'Este enlace expira cuando cierres el navegador.\n\n'
                    f'Si no solicitaste esto, ignora este mensaje.\n\n'
                    f'— Equipo CYS Ltda'
                ),
                from_email='CYS Ltda <ccanariasogamoso@gmail.com>',
                recipient_list=[usuario.email],
                fail_silently=False,
            )
            return JsonResponse({'ok': True, 'mensaje': f'Enviamos un enlace a {usuario.email}. Revisa tu bandeja.'})
        except Exception:
            return JsonResponse({'ok': False, 'error': 'Error al enviar el correo. Intenta de nuevo.'})

    return JsonResponse({'ok': False, 'error': 'Petición inválida.'})


def restablecer_clave(request, token):
    usuario_pk = request.session.get(f'reset_token_{token}')

    if not usuario_pk:
        return render(request, 'restablecer_clave.html', {'error': 'El enlace no es válido o ya expiró.'})

    if request.method == 'POST':
        nueva     = request.POST.get('nueva_clave', '')
        confirmar = request.POST.get('confirmar', '')

        if len(nueva) < 6:
            return render(request, 'restablecer_clave.html', {
                'token': token,
                'error': 'La contraseña debe tener al menos 6 caracteres.'
            })

        if nueva != confirmar:
            return render(request, 'restablecer_clave.html', {
                'token': token,
                'error': 'Las contraseñas no coinciden.'
            })

        try:
            usuario = Usuario.objects.get(pk=usuario_pk)
            usuario.clave = hashlib.sha256(nueva.encode()).hexdigest()
            usuario.save()
            del request.session[f'reset_token_{token}']
            return render(request, 'restablecer_clave.html', {'exito': True})
        except Usuario.DoesNotExist:
            return render(request, 'restablecer_clave.html', {'error': 'Usuario no encontrado.'})

    return render(request, 'restablecer_clave.html', {'token': token})