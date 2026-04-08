from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
from .models import Usuario
from .forms import UsuarioForm
import hashlib
import ssl
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_USER = 'ccanariasogamoso@gmail.com'
EMAIL_PASS = 'jmcikwsvajdmbzab'


def _enviar_correo(destinatario, asunto, cuerpo):
    mensaje = MIMEMultipart()
    mensaje['Subject'] = asunto
    mensaje['From']    = f'CYS Ltda <{EMAIL_USER}>'
    mensaje['To']      = destinatario
    mensaje.attach(MIMEText(cuerpo, 'plain'))

    contexto = ssl.create_default_context()
    contexto.check_hostname = False
    contexto.verify_mode    = ssl.CERT_NONE

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.ehlo()
        server.starttls(context=contexto)
        server.ehlo()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.sendmail(EMAIL_USER, destinatario, mensaje.as_string())


def _validar_clave_segura(clave):
    """Retorna mensaje de error o None si es válida."""
    if len(clave) < 6:
        return 'La contraseña debe tener al menos 6 caracteres.'
    if len(re.findall(r'\d', clave)) < 2:
        return 'La contraseña debe contener al menos 2 números.'
    if not re.search(r'[A-Z]', clave):
        return 'La contraseña debe contener al menos 1 letra mayúscula.'
    return None


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

        # Token con expiración de 15 minutos guardado en BD
        token  = get_random_string(32)
        expira = timezone.now() + timedelta(minutes=15)
        usuario.reset_token        = token
        usuario.reset_token_expira = expira
        usuario.save(update_fields=['reset_token', 'reset_token_expira'])

        link = request.build_absolute_uri(f'/usuario/restablecer/{token}/')

        cuerpo = (
            f'Hola {usuario.nombre},\n\n'
            f'Recibimos una solicitud para restablecer tu contraseña.\n\n'
            f'Haz clic en el siguiente enlace (válido por 15 minutos):\n{link}\n\n'
            f'Si no solicitaste esto, ignora este mensaje.\n\n'
            f'— Equipo CYS Ltda'
        )

        try:
            _enviar_correo(
                destinatario=usuario.email,
                asunto='Recuperación de contraseña — CYS Ltda',
                cuerpo=cuerpo,
            )
            return JsonResponse({'ok': True, 'mensaje': f'Enviamos un enlace a {usuario.email}. Válido por 15 minutos.'})
        except Exception as e:
            print(f"ERROR EMAIL: {type(e).__name__}: {e}")
            return JsonResponse({'ok': False, 'error': f'Error al enviar: {type(e).__name__}: {e}'})

    return JsonResponse({'ok': False, 'error': 'Petición inválida.'})


def restablecer_clave(request, token):
    # Buscar token en BD y verificar expiración
    try:
        usuario = Usuario.objects.get(reset_token=token, activo=True)
    except Usuario.DoesNotExist:
        return render(request, 'restablecer_clave.html', {
            'error': 'El enlace no es válido o ya fue utilizado.'
        })

    if timezone.now() > usuario.reset_token_expira:
        # Limpiar token vencido
        usuario.reset_token        = None
        usuario.reset_token_expira = None
        usuario.save(update_fields=['reset_token', 'reset_token_expira'])
        return render(request, 'restablecer_clave.html', {
            'error': 'El enlace expiró. Solicita uno nuevo.'
        })

    if request.method == 'POST':
        nueva     = request.POST.get('nueva_clave', '')
        confirmar = request.POST.get('confirmar', '')

        error = _validar_clave_segura(nueva)
        if error:
            return render(request, 'restablecer_clave.html', {
                'token': token, 'error': error
            })

        if nueva != confirmar:
            return render(request, 'restablecer_clave.html', {
                'token': token, 'error': 'Las contraseñas no coinciden.'
            })

        usuario.clave              = hashlib.sha256(nueva.encode()).hexdigest()
        usuario.reset_token        = None
        usuario.reset_token_expira = None
        usuario.save(update_fields=['clave', 'reset_token', 'reset_token_expira'])

        return render(request, 'restablecer_clave.html', {'exito': True})

    return render(request, 'restablecer_clave.html', {'token': token})