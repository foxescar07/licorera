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
    if len(clave) < 6:
        return 'La contraseña debe tener al menos 6 caracteres.'
    if len(re.findall(r'\d', clave)) < 2:
        return 'La contraseña debe contener al menos 2 números.'
    if not re.search(r'[A-Z]', clave):
        return 'La contraseña debe contener al menos 1 letra mayúscula.'
    return None
 
 
def _solo_admin(request):
    return request.session.get('usuario_rol') == 'admin'
 
 
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
    response = redirect('login')
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response
 
 
def lista_usuarios(request):
    if not request.session.get('usuario_id'):
        return redirect('login')
    # ── FIX: descarta mensajes de otras apps (ej: ventas) para que no aparezcan aquí
    list(messages.get_messages(request))
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
 
 
def editar_usuario(request, pk):
    if not request.session.get('usuario_id'):
        return redirect('login')
    if not _solo_admin(request):
        return JsonResponse({'ok': False, 'error': 'Sin permisos.'}, status=403)
 
    try:
        u = Usuario.objects.get(pk=pk)
    except Usuario.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Usuario no encontrado.'}, status=404)
 
    if request.method == 'GET':
        return JsonResponse({
            'ok': True,
            'pk':            u.pk,
            'nombre':        u.nombre,
            'apellidos':     u.apellidos,
            'email':         u.email or '',
            'usuario':       u.usuario,
            'tipo_id':       u.tipo_id,
            'tipo_id_label': u.get_tipo_id_display(),
            'identificacion': u.identificacion,
            'rol':           u.rol,
            'rol_label':     u.get_rol_display(),
            'activo':        u.activo,
            'fecha_registro': u.fecha_registro.strftime('%d/%m/%Y'),
        })
 
    if request.method == 'POST':
        nombre        = request.POST.get('nombre', '').strip()
        apellidos     = request.POST.get('apellidos', '').strip()
        email         = request.POST.get('email', '').strip().lower()
        rol           = request.POST.get('rol', '').strip()
        clave_nueva   = request.POST.get('clave_nueva', '').strip()
 
        if not nombre or not apellidos:
            return JsonResponse({'ok': False, 'error': 'Nombre y apellidos son obligatorios.'})
        if any(c.isdigit() for c in nombre):
            return JsonResponse({'ok': False, 'error': 'El nombre no debe contener números.'})
        if any(c.isdigit() for c in apellidos):
            return JsonResponse({'ok': False, 'error': 'Los apellidos no deben contener números.'})
        if rol not in ['admin', 'cajero', 'empleado']:
            return JsonResponse({'ok': False, 'error': 'Rol inválido.'})
        if email and email != (u.email or '').lower():
            if Usuario.objects.filter(email__iexact=email).exclude(pk=u.pk).exists():
                return JsonResponse({'ok': False, 'error': 'Este correo ya está en uso.'})
 
        if clave_nueva:
            err = _validar_clave_segura(clave_nueva)
            if err:
                return JsonResponse({'ok': False, 'error': err})
 
        fields = ['nombre', 'apellidos', 'email', 'rol']
        u.nombre    = nombre
        u.apellidos = apellidos
        u.email     = email or None
        u.rol       = rol
 
        if clave_nueva:
            u.clave = hashlib.sha256(clave_nueva.encode()).hexdigest()
            fields.append('clave')
 
        u.save(update_fields=fields)
        return JsonResponse({
            'ok': True,
            'mensaje': f'Usuario {u.usuario} actualizado correctamente.',
            'nombre_completo': u.nombre_completo,
            'rol_label': u.get_rol_display(),
        })
 
    return JsonResponse({'ok': False, 'error': 'Método no permitido.'})
 
 
def toggle_activo(request, pk):
    if not request.session.get('usuario_id'):
        return redirect('login')
    if not _solo_admin(request):
        return JsonResponse({'ok': False, 'error': 'Sin permisos.'}, status=403)
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Método no permitido.'})
    try:
        u = Usuario.objects.get(pk=pk)
    except Usuario.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Usuario no encontrado.'})
 
    if u.pk == request.session.get('usuario_id'):
        return JsonResponse({'ok': False, 'error': 'No puedes desactivar tu propia cuenta.'})
 
    u.activo = not u.activo
    u.save(update_fields=['activo'])
    return JsonResponse({
        'ok': True,
        'activo': u.activo,
        'mensaje': f'Usuario {"activado" if u.activo else "desactivado"} correctamente.',
    })
 
 
def solicitar_recuperacion(request):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        correo = request.POST.get('correo', '').strip().lower()
        try:
            usuario = Usuario.objects.get(email__iexact=correo, activo=True)
        except Usuario.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'No existe una cuenta activa con ese correo.'})
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
    try:
        usuario = Usuario.objects.get(reset_token=token, activo=True)
    except Usuario.DoesNotExist:
        return render(request, 'restablecer_clave.html', {
            'error': 'El enlace no es válido o ya fue utilizado.'
        })
    if timezone.now() > usuario.reset_token_expira:
        Usuario.objects.filter(pk=usuario.pk).update(
            reset_token=None, reset_token_expira=None
        )
        return render(request, 'restablecer_clave.html', {
            'error': 'El enlace expiró. Solicita uno nuevo.'
        })
    if request.method == 'POST':
        nueva     = request.POST.get('nueva_clave', '')
        confirmar = request.POST.get('confirmar', '')
        error = _validar_clave_segura(nueva)
        if error:
            return render(request, 'restablecer_clave.html', {'token': token, 'error': error})
        if nueva != confirmar:
            return render(request, 'restablecer_clave.html', {
                'token': token, 'error': 'Las contraseñas no coinciden.'
            })
        nueva_hash = hashlib.sha256(nueva.encode()).hexdigest()
        Usuario.objects.filter(pk=usuario.pk).update(
            clave=nueva_hash, reset_token=None, reset_token_expira=None
        )
        return render(request, 'restablecer_clave.html', {'exito': True})
    return render(request, 'restablecer_clave.html', {'token': token})
 
 
def perfil_datos(request):
    if not request.session.get('usuario_id'):
        return JsonResponse({'ok': False, 'error': 'Sin sesión.'})
    try:
        u = Usuario.objects.get(pk=request.session['usuario_id'])
        return JsonResponse({
            'ok': True,
            'nombre':         u.nombre,
            'apellidos':      u.apellidos,
            'usuario':        u.usuario,
            'email':          u.email or '',
            'tipo_id':        u.tipo_id,
            'tipo_id_label':  u.get_tipo_id_display(),
            'identificacion': u.identificacion,
            'rol':            u.rol,
            'rol_label':      u.get_rol_display(),
            'fecha_registro': u.fecha_registro.strftime('%d/%m/%Y'),
        })
    except Usuario.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Usuario no encontrado.'})
 
 
def perfil_editar(request):
    if not request.session.get('usuario_id'):
        return JsonResponse({'ok': False, 'error': 'Sin sesión.'})
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Método no permitido.'})
    try:
        u = Usuario.objects.get(pk=request.session['usuario_id'])
    except Usuario.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Usuario no encontrado.'})
 
    nombre       = request.POST.get('nombre', '').strip()
    apellidos    = request.POST.get('apellidos', '').strip()
    email        = request.POST.get('email', '').strip().lower()
    clave_nueva  = request.POST.get('clave_nueva', '').strip()
    clave_actual = request.POST.get('clave_actual', '').strip()
 
    if not nombre or not apellidos:
        return JsonResponse({'ok': False, 'error': 'Nombre y apellidos son obligatorios.'})
    if any(c.isdigit() for c in nombre):
        return JsonResponse({'ok': False, 'error': 'El nombre no debe contener números.'})
    if any(c.isdigit() for c in apellidos):
        return JsonResponse({'ok': False, 'error': 'Los apellidos no deben contener números.'})
    if email and email != (u.email or '').lower():
        if Usuario.objects.filter(email__iexact=email).exclude(pk=u.pk).exists():
            return JsonResponse({'ok': False, 'error': 'Este correo ya está en uso.'})
    if clave_nueva:
        if not clave_actual:
            return JsonResponse({'ok': False, 'error': 'Ingresa tu contraseña actual para cambiarla.'})
        if u.clave != hashlib.sha256(clave_actual.encode()).hexdigest():
            return JsonResponse({'ok': False, 'error': 'La contraseña actual es incorrecta.'})
        err = _validar_clave_segura(clave_nueva)
        if err:
            return JsonResponse({'ok': False, 'error': err})
 
    fields = ['nombre', 'apellidos', 'email']
    u.nombre    = nombre
    u.apellidos = apellidos
    u.email     = email or None
    if clave_nueva:
        u.clave = hashlib.sha256(clave_nueva.encode()).hexdigest()
        fields.append('clave')
    u.save(update_fields=fields)
    request.session['usuario_nombre'] = u.nombre_completo
    return JsonResponse({
        'ok': True,
        'mensaje': 'Perfil actualizado correctamente.',
        'nombre_completo': u.nombre_completo,
    })
 
 
def eliminar_usuario(request, pk):
    if request.session.get('usuario_rol') != 'admin':
        return JsonResponse({'ok': False, 'error': 'Sin permiso.'})
    if request.method != 'POST':
        return JsonResponse({'ok': False})
    try:
        u = Usuario.objects.get(pk=pk)
        if u.activo:
            return JsonResponse({'ok': False, 'error': 'Solo se pueden eliminar usuarios inactivos.'})
        if u.pk == request.session.get('usuario_id'):
            return JsonResponse({'ok': False, 'error': 'No puedes eliminarte a ti mismo.'})
        u.delete()
        return JsonResponse({'ok': True})
    except Usuario.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Usuario no encontrado.'})